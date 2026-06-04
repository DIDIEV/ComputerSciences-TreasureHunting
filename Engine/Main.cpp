#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>
#include <cmath>

#include "nlohmann/json.hpp"
#include "linked_list.h"
#include "tree.h"

using json = nlohmann::json;

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------
static const int GRID_ROWS = 8;
static const int GRID_COLS = 8;

// ---------------------------------------------------------------------------
// Utility helpers
// ---------------------------------------------------------------------------

// Safe file reader — returns empty string on failure
static std::string readFile(const std::string& path) {
    std::ifstream f(path);
    if (!f.is_open()) return "";
    std::ostringstream ss;
    ss << f.rdbuf();
    return ss.str();
}

// Safe file writer
static bool writeFile(const std::string& path, const std::string& content) {
    std::ofstream f(path);
    if (!f.is_open()) return false;
    f << content;
    return true;
}

// Manhattan distance between two grid cells
static int manhattan(int r1, int c1, int r2, int c2) {
    return std::abs(r1 - r2) + std::abs(c1 - c2);
}

// Check bounds
static bool inBounds(int r, int c) {
    return r >= 0 && r < GRID_ROWS && c >= 0 && c < GRID_COLS;
}

// ---------------------------------------------------------------------------
// GameState — holds everything the engine needs between calls
// The engine is stateless between processes; state.json is the persistence.
// ---------------------------------------------------------------------------
struct GameState {
    // Player
    int  playerRow     = 0;
    int  playerCol     = 0;
    int  stepsTaken    = 0;
    int  stepLimit     = 30;          // Backtracking constraint
    int  score         = 0;
    bool gameOver      = false;
    bool playerWon     = false;
    std::string message = "Game started. Find the treasures!";

    // Grid obstacles (walls): list of {row, col}
    std::vector<std::pair<int,int>> walls;

    // Treasures loaded from input at game-start
    // kept here so we can rebuild the BST each engine call
    struct TreasureRecord {
        int id, value, row, col;
        std::string name;
        bool collected;
    };
    std::vector<TreasureRecord> treasures;
};

// ---------------------------------------------------------------------------
// Load GameState from state.json (persisted from last engine call)
// On very first call state.json either doesn't exist or has "init":true
// ---------------------------------------------------------------------------
static GameState loadState(const std::string& statePath) {
    GameState gs;
    std::string raw = readFile(statePath);
    if (raw.empty()) return gs;   // First run — use defaults

    try {
        json j = json::parse(raw);

        if (j.contains("init") && j["init"].get<bool>()) return gs;

        gs.playerRow  = j.value("player_row",  0);
        gs.playerCol  = j.value("player_col",  0);
        gs.stepsTaken = j.value("steps_taken", 0);
        gs.stepLimit  = j.value("step_limit",  30);
        gs.score      = j.value("score",       0);
        gs.gameOver   = j.value("game_over",   false);
        gs.playerWon  = j.value("player_won",  false);
        gs.message    = j.value("message",     "");

        if (j.contains("walls")) {
            for (auto& w : j["walls"]) {
                gs.walls.push_back({w["row"].get<int>(), w["col"].get<int>()});
            }
        }

        if (j.contains("treasures")) {
            for (auto& t : j["treasures"]) {
                GameState::TreasureRecord tr;
                tr.id        = t.value("id",        0);
                tr.value     = t.value("value",      0);
                tr.row       = t.value("row",        0);
                tr.col       = t.value("col",        0);
                tr.name      = t.value("name",       "Treasure");
                tr.collected = t.value("collected",  false);
                gs.treasures.push_back(tr);
            }
        }
    } catch (...) {
        // Corrupted state — reset
        std::cerr << "[engine] Warning: could not parse state.json, resetting." << std::endl;
    }
    return gs;
}
static void populateBST(TreasureBST& bst, const GameState& gs) {
    for (auto& tr : gs.treasures) {
        bst.insert(tr.id, tr.value, tr.row, tr.col, tr.name);
        if (tr.collected) bst.collect(tr.id);
    }
}

// ---------------------------------------------------------------------------
// Check whether a cell is a wall
// ---------------------------------------------------------------------------
static bool isWall(const GameState& gs, int r, int c) {
    for (auto& w : gs.walls)
        if (w.first == r && w.second == c) return true;
    return false;
}

static std::string processAction(GameState& gs, TreasureBST& bst,
                                  MovementList& hist, const json& action) {
    if (gs.gameOver)
        return "Game is already over. Please restart.";

    std::string type = action.value("type", "none");

    // ---- INIT action: Python calls this on new game ----------------------
    if (type == "init") {
        gs.playerRow  = action.value("player_row", 0);
        gs.playerCol  = action.value("player_col", 0);
        gs.stepLimit  = action.value("step_limit", 30);
        gs.stepsTaken = 0;
        gs.score      = 0;
        gs.gameOver   = false;
        gs.playerWon  = false;
        gs.treasures.clear();
        gs.walls.clear();

        if (action.contains("walls")) {
            for (auto& w : action["walls"])
                gs.walls.push_back({w["row"].get<int>(), w["col"].get<int>()});
        }

        if (action.contains("treasures")) {
            for (auto& t : action["treasures"]) {
                GameState::TreasureRecord tr;
                tr.id        = t.value("id",       0);
                tr.value     = t.value("value",    0);
                tr.row       = t.value("row",      0);
                tr.col       = t.value("col",      0);
                tr.name      = t.value("name",     "Treasure");
                tr.collected = false;
                gs.treasures.push_back(tr);
                bst.insert(tr.id, tr.value, tr.row, tr.col, tr.name);
            }
        }

        hist.append(gs.playerRow, gs.playerCol, 0);
        return "New game initialised. Good luck!";
    }

    // ---- MOVE action -------------------------------------------------------
    if (type == "move") {
        std::string dir = action.value("direction", "");
        int nr = gs.playerRow;
        int nc = gs.playerCol;

        if      (dir == "up")    --nr;
        else if (dir == "down")  ++nr;
        else if (dir == "left")  --nc;
        else if (dir == "right") ++nc;
        else return "Unknown direction: " + dir;

        if (!inBounds(nr, nc))
            return "Cannot move " + dir + ": out of bounds.";

        if (isWall(gs, nr, nc))
            return "Cannot move " + dir + ": wall in the way.";

        gs.playerRow  = nr;
        gs.playerCol  = nc;
        gs.stepsTaken++;
        hist.append(nr, nc, gs.stepsTaken);

        // ---- Treasure collection check ------------------------------------
        std::string collectMsg = "";
        for (auto& tr : gs.treasures) {
            if (!tr.collected && tr.row == nr && tr.col == nc) {
                tr.collected = true;
                bst.collect(tr.id);
                gs.score += tr.value;
                collectMsg = " Collected \"" + tr.name + "\" (+" +
                             std::to_string(tr.value) + " pts)!";
                break;
            }
        }

        // ---- Win condition: all treasures collected -----------------------
        if (bst.countUncollected() == 0) {
            gs.gameOver  = true;
            gs.playerWon = true;
            return "You collected ALL treasures! Final score: " +
                   std::to_string(gs.score) + ". You WIN!" + collectMsg;
        }

        // ---- Loss condition: step limit exceeded --------------------------
        if (gs.stepsTaken >= gs.stepLimit) {
            gs.gameOver  = true;
            gs.playerWon = false;
            return "Step limit reached (" + std::to_string(gs.stepLimit) +
                   " steps). Game Over. Score: " + std::to_string(gs.score) +
                   "." + collectMsg;
        }

        // ---- Greedy hint: nearest highest-value uncollected treasure ------
        TreasureNode* best = bst.findMaxUncollected();
        std::string hint   = "";
        if (best != nullptr) {
            int dist = manhattan(gs.playerRow, gs.playerCol, best->row, best->col);
            hint = " Hint -> nearest high-value target: \"" + best->name +
                   "\" (val=" + std::to_string(best->value) +
                   ") at (" + std::to_string(best->row) + "," +
                   std::to_string(best->col) + "), dist=" +
                   std::to_string(dist) + ".";
        }

        return "Moved " + dir + " to (" + std::to_string(nr) + "," +
               std::to_string(nc) + "). Steps: " +
               std::to_string(gs.stepsTaken) + "/" +
               std::to_string(gs.stepLimit) + "." + collectMsg + hint;
    }

    // ---- QUERY: ask engine for the greedy suggestion ---------------------
    if (type == "query_best_treasure") {
        TreasureNode* best = bst.findMaxUncollected();
        if (best == nullptr) return "No uncollected treasures remaining.";
        int dist = manhattan(gs.playerRow, gs.playerCol, best->row, best->col);
        return "Best target: \"" + best->name +
               "\" value=" + std::to_string(best->value) +
               " at (" + std::to_string(best->row) + "," +
               std::to_string(best->col) + "), manhattan dist=" +
               std::to_string(dist) + ".";
    }

    // ---- RESTART ---------------------------------------------------------
    if (type == "restart") {
        gs = GameState();
        return "Engine reset. Send an 'init' action to start a new game.";
    }

    return "Unknown action type: " + type;
}

// ---------------------------------------------------------------------------
// Serialize full GameState + data structures to state.json
// ---------------------------------------------------------------------------
static json buildStateJson(const GameState& gs, const TreasureBST& bst,
                            const MovementList& hist, const std::string& msg) {
    json j;

    // Player & game meta
    j["player_row"]  = gs.playerRow;
    j["player_col"]  = gs.playerCol;
    j["steps_taken"] = gs.stepsTaken;
    j["step_limit"]  = gs.stepLimit;
    j["score"]       = gs.score;
    j["game_over"]   = gs.gameOver;
    j["player_won"]  = gs.playerWon;
    j["message"]     = msg;

    // Grid dimensions (Python uses these to draw the board)
    j["grid_rows"] = GRID_ROWS;
    j["grid_cols"] = GRID_COLS;

    // Walls
    j["walls"] = json::array();
    for (auto& w : gs.walls) {
        json wj;
        wj["row"] = w.first;
        wj["col"] = w.second;
        j["walls"].push_back(wj);
    }

    // Treasures (full list with collected flag — Python renders them)
    j["treasures"] = json::array();
    for (auto& tr : gs.treasures) {
        json tj;
        tj["id"]        = tr.id;
        tj["value"]     = tr.value;
        tj["row"]       = tr.row;
        tj["col"]       = tr.col;
        tj["name"]      = tr.name;
        tj["collected"] = tr.collected;
        j["treasures"].push_back(tj);
    }

    // Stats from data structures (BST and linked list)
    j["bst_height"]        = bst.height();
    j["bst_node_count"]    = bst.getNodeCount();
    j["uncollected_count"] = bst.countUncollected();
    j["history_length"]    = hist.getSize();

    // Greedy suggestion (Python can display this in HUD)
    TreasureNode* best = bst.findMaxUncollected();
    if (best != nullptr) {
        j["greedy_target"] = {
            {"id",    best->treasureId},
            {"name",  best->name},
            {"value", best->value},
            {"row",   best->row},
            {"col",   best->col},
            {"dist",  manhattan(gs.playerRow, gs.playerCol,
                                best->row, best->col)}
        };
    } else {
        j["greedy_target"] = nullptr;
    }

    return j;
}

// ---------------------------------------------------------------------------
// main
// ---------------------------------------------------------------------------
int main(int argc, char* argv[]) {
    // Allow overriding paths via CLI args (useful for testing)
    std::string inputPath = "../data/input.json";
    std::string statePath = "../data/state.json";
    if (argc >= 3) {
        inputPath = argv[1];
        statePath = argv[2];
    }

    // 1. Read input.json
    std::string inputRaw = readFile(inputPath);
    if (inputRaw.empty()) {
        std::cerr << "[engine] ERROR: cannot read input file: " << inputPath << std::endl;
        return 1;
    }

    json inputJson;
    try {
        inputJson = json::parse(inputRaw);
    } catch (const std::exception& e) {
        std::cerr << "[engine] ERROR: malformed input.json — " << e.what() << std::endl;
        return 1;
    }

    // 2. Load persisted game state from state.json
    GameState gs = loadState(statePath);

    // 3. Rebuild data structures from persisted state
    TreasureBST  bst;
    MovementList hist;
    populateBST(bst, gs);
    // Note: movement history is not replayed from state (too large);
    // we only carry the count for display. Each engine process adds its step.
    // If you want full replay, extend state.json with the history array.

    // 4. Process the action
    std::string msg = processAction(gs, bst, hist, inputJson);
    gs.message = msg;

    // 5. Build and write state.json
    json stateJson = buildStateJson(gs, bst, hist, msg);
    std::string stateStr = stateJson.dump(2);  // pretty-printed, 2-space indent

    if (!writeFile(statePath, stateStr)) {
        std::cerr << "[engine] ERROR: cannot write state file: " << statePath << std::endl;
        return 1;
    }

    std::cout << "[engine] OK | " << msg << std::endl;
    return 0;
}