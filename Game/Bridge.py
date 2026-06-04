"""
DISTRITAL FRANCISCO JOSÉ DE CALDAS UNIVERSITY
COURSE: COMPUTER SCIENCES I (2026-I)

PROJECT: TREASURE HUNT
COMPONENT: INTERACTIVE PYGAME USER INTERFACE
"""

import json
import os
import subprocess

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", "Data"))
ENGINE_EXE = os.path.abspath(os.path.join(CURRENT_DIR, "..", "Engine", "Main.exe"))
INPUT_PATH = os.path.join(DATA_DIR, "input.json")
STATE_PATH = os.path.join(DATA_DIR, "state.json")
DEFAULT_GRID_ROWS = 10
DEFAULT_GRID_COLS = 10

def _load_json(path):
    if not os.path.exists(path):
        return None
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None


def _write_json(path, payload):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(payload, f, indent=4)


def _build_engine_payload(action_type, details=None):
    details = details or {}
    if action_type == "MOVE":
        return {
            "type": "move",
            "direction": details.get("dir", "").lower()
        }
    if action_type == "RUN_GREEDY":
        return {
            "type": "query_best_treasure"
        }
    if action_type == "RUN_BACKTRACKING":
        return {
            "type": "run_backtracking",
            "step_limit": details.get("step_limit", 10)
        }
    return None


def _init_default_state():
    return {
        "player_row": 0,
        "player_col": 0,
        "steps_taken": 0,
        "step_limit": 40,
        "score": 0,
        "game_over": False,
        "player_won": False,
        "message": "Waiting for engine first run.",
        "grid_rows": DEFAULT_GRID_ROWS,
        "grid_cols": DEFAULT_GRID_COLS,
        "walls": [],
        "treasures": [
            {"id": 1, "value": 100, "row": 1, "col": 3, "name": "Bronze Chest", "collected": False},
            {"id": 2, "value": 250, "row": 2, "col": 6, "name": "Silver Crown", "collected": False},
            {"id": 3, "value": 450, "row": 4, "col": 1, "name": "Golden Chalice", "collected": False},
            {"id": 4, "value": 300, "row": 7, "col": 8, "name": "Emerald Ring", "collected": False}
        ],
        "bst_height": 0,
        "bst_node_count": 4,
        "uncollected_count": 4,
        "history_length": 0,
        "greedy_target": None,
        "movement_history": ["START"],
        "init": True
    }


def _process_action_locally(action):
    state = _load_json(STATE_PATH) or _init_default_state()
    action_type = action.get("type", "")

    if action_type == "move":
        direction = action.get("direction", "").lower()
        row = state.get("player_row", 0)
        col = state.get("player_col", 0)
        if direction == "up":
            row -= 1
        elif direction == "down":
            row += 1
        elif direction == "left":
            col -= 1
        elif direction == "right":
            col += 1
        else:
            state["message"] = f"Unknown direction: {direction}"
            _write_json(STATE_PATH, state)
            return

        max_rows = state.get("grid_rows", DEFAULT_GRID_ROWS)
        max_cols = state.get("grid_cols", DEFAULT_GRID_COLS)
        if row < 0 or row >= max_rows or col < 0 or col >= max_cols:
            state["message"] = f"Cannot move {direction}: out of bounds."
            _write_json(STATE_PATH, state)
            return

        if any(w.get("row") == row and w.get("col") == col for w in state.get("walls", [])):
            state["message"] = f"Cannot move {direction}: wall in the way."
            _write_json(STATE_PATH, state)
            return

        state["player_row"] = row
        state["player_col"] = col
        state["steps_taken"] = state.get("steps_taken", 0) + 1
        collected_message = ""
        for treasure in state.get("treasures", []):
            if not treasure.get("collected", False) and treasure.get("row") == row and treasure.get("col") == col:
                treasure["collected"] = True
                state["score"] = state.get("score", 0) + treasure.get("value", 0)
                collected_message = f" Collected \"{treasure.get('name', 'Treasure')}\" (+{treasure.get('value', 0)} pts)!"
                break

        if state.get("treasures") and all(t.get("collected", False) for t in state.get("treasures", [])):
            state["game_over"] = True
            state["player_won"] = True
            state["message"] = f"You collected ALL treasures! Final score: {state.get('score', 0)}.{collected_message}"
        elif state["steps_taken"] >= state.get("step_limit", 40):
            state["game_over"] = True
            state["player_won"] = False
            state["message"] = f"Step limit reached ({state.get('step_limit', 40)} steps). Game Over. Score: {state.get('score', 0)}.{collected_message}"
        else:
            state["message"] = f"Moved {direction} to ({row},{col}). Steps: {state.get('steps_taken')} / {state.get('step_limit')}.{collected_message}"

    elif action_type == "query_best_treasure":
        treasures = [t for t in state.get("treasures", []) if not t.get("collected", False)]
        if not treasures:
            state["message"] = "No uncollected treasures remaining."
        else:
            best = max(treasures, key=lambda t: t.get("value", 0))
            row = state.get("player_row", 0)
            col = state.get("player_col", 0)
            dist = abs(best.get("row", 0) - row) + abs(best.get("col", 0) - col)
            state["message"] = f"Best target: \"{best.get('name')}\" value={best.get('value')} at ({best.get('row')},{best.get('col')}), manhattan dist={dist}."

    elif action_type == "run_backtracking":
        state["message"] = "Backtracking is not available in the local fallback engine."

    elif action_type == "init":
        state = {
            "player_row": action.get("player_row", 0),
            "player_col": action.get("player_col", 0),
            "steps_taken": 0,
            "step_limit": action.get("step_limit", 40),
            "score": 0,
            "game_over": False,
            "player_won": False,
            "message": "New game initialised.",
            "grid_rows": action.get("grid_rows", DEFAULT_GRID_ROWS),
            "grid_cols": action.get("grid_cols", DEFAULT_GRID_COLS),
            "walls": action.get("walls", []),
            "treasures": [{**t, "collected": False} for t in action.get("treasures", [])],
            "bst_height": 0,
            "bst_node_count": len(action.get("treasures", [])),
            "uncollected_count": len(action.get("treasures", [])),
            "history_length": 0,
            "greedy_target": None,
            "init": False
        }

    else:
        state["message"] = f"Unknown action type: {action_type}"

    state["init"] = False
    _write_json(STATE_PATH, state)


def _run_engine(payload):
    if os.path.exists(ENGINE_EXE):
        try:
            subprocess.run([ENGINE_EXE, INPUT_PATH, STATE_PATH], cwd=os.path.dirname(ENGINE_EXE), check=True)
        except Exception:
            _process_action_locally(payload)
    else:
        _process_action_locally(payload)


def _convert_for_ui(state):
    if state is None:
        return {
            "player_pos": [0, 0],
            "score": 0,
            "movement_history": ["START"],
            "treasures": []
        }

    return {
        "player_pos": [state.get("player_col", 0), state.get("player_row", 0)],
        "score": state.get("score", 0),
        "movement_history": state.get("movement_history", []),
        "treasures": [
            {
                "x": t.get("col", 0),
                "y": t.get("row", 0),
                "value": t.get("value", 0),
                "name": t.get("name", "Treasure")
            }
            for t in state.get("treasures", [])
            if not t.get("collected", False)
        ]
    }


def _ensure_initialized_state():
    state = _load_json(STATE_PATH)
    if state is None or state.get("init", False):
        input_action = _load_json(INPUT_PATH)
        if input_action is not None:
            _run_engine(input_action)
            state = _load_json(STATE_PATH)
        else:
            state = _init_default_state()
            _write_json(STATE_PATH, state)
    return state


def save_user_action(action_type, details=None):
    payload = _build_engine_payload(action_type, details)
    if payload is None:
        return
    _write_json(INPUT_PATH, payload)
    _run_engine(payload)


def read_game_state():
    state = _ensure_initialized_state()
    if state is None:
        return {
            "player_pos": [0, 0],
            "score": 0,
            "movement_history": ["START"],
            "treasures": []
        }
    return _convert_for_ui(state)


