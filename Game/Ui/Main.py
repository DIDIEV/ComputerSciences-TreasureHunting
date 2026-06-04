"""
DISTRITAL FRANCISCO JOSÉ DE CALDAS UNIVERSITY
COURSE: COMPUTER SCIENCES I (2026-I)

PROJECT: TREASURE HUNT
COMPONENT: INTERACTIVE PYGAME USER INTERFACE
"""

import os
import sys
import pygame
import random
import time
import json

# Dynamic path injection to safely import Bridge and algorithms across parent packages
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
sys.path.append(PARENT_DIR)

import Bridge  
from Algorithms.Greedy import find_best_treasure_greedy
from Algorithms.Backtracking import plan_path_backtracking

# Initialize the graphics library frame context
pygame.init()

# Viewport spatial definitions (Constraint: Matrix grid layout must be at least 8x8)
CELL_SIZE = 60
DEFAULT_GRID_SIZE = 8
HUD_WIDTH = 260
WINDOW_WIDTH = (DEFAULT_GRID_SIZE * CELL_SIZE) + HUD_WIDTH
WINDOW_HEIGHT = DEFAULT_GRID_SIZE * CELL_SIZE

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Treasure Hunt Simulation - Python/C++ Interfacing")
frame_clock = pygame.time.Clock()

# Structural UI color palette (RGB scheme)
COLOR_BG = (24, 24, 27)         # Slate-900 background dark theme
COLOR_GRID = (39, 39, 42)       # Slate-800 grid board lines
COLOR_PLAYER = (59, 130, 246)   # Blue-500 interactive agent block
COLOR_TREASURE_LOW = (52, 211, 153)   # Green-400 low-value treasure
COLOR_TREASURE_MEDIUM = (234, 179, 8) # Yellow-500 medium-value treasure
COLOR_TREASURE_HIGH = (239, 68, 68)   # Red-500 high-value treasure
COLOR_TEXT = (244, 244, 245)    # Zinc-100 high contrast layout text
COLOR_HUD_BG = (39, 39, 42)     # Sidebar contrast container panel
COLOR_TRAP = (220, 38, 38)     # Red-600 trap color
COLOR_BACKTRACK_ROUTE = (16, 185, 129)

# Trap spawn timing (use Bridge constant when available)
TRAP_SPAWN_INTERVAL = getattr(Bridge, 'TRAP_SPAWN_INTERVAL', 20)
_trap = None
_last_trap_spawn = time.time()
BACKTRACKING_MAX_USES = 5


def treasure_color_by_value(value: int):
    if value <= 20:
        return COLOR_TREASURE_LOW
    if value <= 60:
        return COLOR_TREASURE_MEDIUM
    return COLOR_TREASURE_HIGH

def draw_matrix_board(rows: int, cols: int):
    """
    Renders the dynamic board grid layout using the current state dimensions.
    """
    board_width = cols * CELL_SIZE
    board_height = rows * CELL_SIZE

    for x in range(0, board_width, CELL_SIZE):
        for y in range(0, board_height, CELL_SIZE):
            cell_rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, COLOR_GRID, cell_rect, 1)


def draw_sidebar_hud(game_state, message=""):
    """
    Renders simulation parameters, player diagnostics, and active log outputs 
    within the structural sidebar container.
    """
    font_body = pygame.font.SysFont("Arial", 16)
    font_header = pygame.font.SysFont("Arial", 18, bold=True)
    font_small = pygame.font.SysFont("Arial", 13)
    
    board_width = game_state.get("grid_cols", DEFAULT_GRID_SIZE) * CELL_SIZE
    board_height = game_state.get("grid_rows", DEFAULT_GRID_SIZE) * CELL_SIZE

    # Render main background panel container
    hud_rect = pygame.Rect(board_width, 0, HUD_WIDTH, board_height)
    pygame.draw.rect(screen, COLOR_HUD_BG, hud_rect)
    
    # Title display
    title_surface = font_header.render("TREASURE HUNT (V7)", True, COLOR_TREASURE_MEDIUM)
    screen.blit(title_surface, (board_width + 20, 20))
    
    # Active simulation data outputs
    pos_text = f"Agent Position: [{game_state['player_pos'][0]}, {game_state['player_pos'][1]}]"
    pos_surface = font_body.render(pos_text, True, COLOR_TEXT)
    screen.blit(pos_surface, (board_width + 20, 60))
    
    score_text = f"Collected Score: {game_state['score']}"
    score_surface = font_body.render(score_text, True, COLOR_TEXT)
    screen.blit(score_surface, (board_width + 20, 90))
    
    items_text = f"Items Remaining: {len(game_state['treasures'])}"
    items_surface = font_body.render(items_text, True, COLOR_TEXT)
    screen.blit(items_surface, (board_width + 20, 120))

    traps_text = f"Traps Active: {len(game_state.get('traps', []))}"
    traps_surface = font_body.render(traps_text, True, COLOR_TRAP)
    screen.blit(traps_surface, (board_width + 20, 140))

    backtracking_text = f"Backtracking left: {game_state.get('backtracking_remaining', BACKTRACKING_MAX_USES)}"
    backtracking_surface = font_body.render(backtracking_text, True, COLOR_TEXT)
    screen.blit(backtracking_surface, (board_width + 20, 160))
    
    # Controls reference text block
    controls_title = font_header.render("CONTROLS:", True, COLOR_TEXT)
    screen.blit(controls_title, (board_width + 20, 180))
    
    arrow_txt = font_small.render("- ARROW KEYS: Manual Step Move", True, COLOR_TEXT)
    screen.blit(arrow_txt, (board_width + 20, 210))
    
    greedy_txt = font_small.render("- 'G' KEY: Execute Greedy Target", True, COLOR_TREASURE_MEDIUM)
    screen.blit(greedy_txt, (board_width + 20, 235))
    
    bt_txt = font_small.render(f"- 'B' KEY: Run Backtracking (Max {BACKTRACKING_MAX_USES} uses)", True, COLOR_PLAYER)
    screen.blit(bt_txt, (board_width + 20, 260))

    # Real-time algorithm logging monitor
    if message:
        log_title = font_header.render("ENGINE LOG:", True, COLOR_TREASURE_MEDIUM)
        screen.blit(log_title, (board_width + 20, 310))
        log_surface = font_small.render(message, True, COLOR_TEXT)
        screen.blit(log_surface, (board_width + 20, 340))


# Application Entry Initialization
application_active = True
active_log_message = "System initialized."

while application_active:
    # Set background baseline color state
    screen.fill(COLOR_BG)
    
    # 1. Pipeline Read Step: Query JSON Bridge interface data from disk
    current_game_state = Bridge.read_game_state()
    board_rows = current_game_state.get("grid_rows", DEFAULT_GRID_SIZE)
    board_cols = current_game_state.get("grid_cols", DEFAULT_GRID_SIZE)
    board_width = board_cols * CELL_SIZE
    board_height = board_rows * CELL_SIZE

    if screen.get_size() != (board_width + HUD_WIDTH, board_height):
        screen = pygame.display.set_mode((board_width + HUD_WIDTH, board_height))

    # Spawn a trap periodically using Bridge helper (fallback, persistent)
    try:
        if time.time() - _last_trap_spawn > TRAP_SPAWN_INTERVAL:
            full_state = Bridge._load_json(Bridge.STATE_PATH) or Bridge._init_default_state()
            new_trap = Bridge._spawn_random_trap(full_state)
            if new_trap:
                Bridge._write_json(Bridge.STATE_PATH, full_state)
            _last_trap_spawn = time.time()
    except Exception:
        # If Bridge internals aren't available, skip spawn
        pass

    draw_matrix_board(board_rows, board_cols)
    
    # 2. Render Board Entities: Render structural states fetched from memory representations
    # Drawing target treasure matrices elements
    # Draw backtracking route overlay if available
    for route_cell in current_game_state.get("backtracking_route", []):
        rx, ry = route_cell.get("x", 0), route_cell.get("y", 0)
        if not (0 <= rx < board_cols and 0 <= ry < board_rows):
            continue
        route_rect = pygame.Rect(rx * CELL_SIZE + 22, ry * CELL_SIZE + 22, CELL_SIZE - 44, CELL_SIZE - 44)
        pygame.draw.rect(screen, COLOR_BACKTRACK_ROUTE, route_rect, 2)
        pygame.draw.circle(screen, COLOR_BACKTRACK_ROUTE, (rx * CELL_SIZE + CELL_SIZE // 2, ry * CELL_SIZE + CELL_SIZE // 2), 4)

    for treasure in current_game_state["treasures"]:
        tx, ty = treasure["x"], treasure["y"]
        if not (0 <= tx < board_cols and 0 <= ty < board_rows):
            continue
        # Choose color by value tier
        color = treasure_color_by_value(treasure.get("value", 0))
        treasure_bounds = pygame.Rect(tx * CELL_SIZE + 15, ty * CELL_SIZE + 15, CELL_SIZE - 30, CELL_SIZE - 30)
        pygame.draw.ellipse(screen, color, treasure_bounds)
        
    # Draw traps (if any)
    for trap in current_game_state.get("traps", []):
        tx, ty = trap.get("x", 0), trap.get("y", 0)
        if not (0 <= tx < board_cols and 0 <= ty < board_rows):
            continue
        trap_rect = pygame.Rect(tx * CELL_SIZE + 18, ty * CELL_SIZE + 18, CELL_SIZE - 36, CELL_SIZE - 36)
        pygame.draw.rect(screen, COLOR_TRAP, trap_rect)

    # Drawing active player agent positioning block
    px, py = current_game_state["player_pos"]
    px = max(0, min(px, board_cols - 1))
    py = max(0, min(py, board_rows - 1))
    player_bounds = pygame.Rect(px * CELL_SIZE + 10, py * CELL_SIZE + 10, CELL_SIZE - 20, CELL_SIZE - 20)
    pygame.draw.rect(screen, COLOR_PLAYER, player_bounds)

    # Check for trap collision (player stepped on a trap)
    for trap in current_game_state.get("traps", []):
        if trap.get("x") == px and trap.get("y") == py:
            try:
                new_state = Bridge._init_default_state()
                new_state["message"] = "Trap triggered! Game reset."
                Bridge._write_json(Bridge.STATE_PATH, new_state)
                active_log_message = "TRAP! Game reset."
            except Exception:
                active_log_message = "TRAP! (reset failed)"
            # Reload state for HUD display
            current_game_state = Bridge.read_game_state()
            break

    # Drawing auxiliary sidebar viewport
    draw_sidebar_hud(current_game_state, active_log_message)
    
    # 3. Handle System Interrupts & Peripheral Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            application_active = False
            
        elif event.type == pygame.KEYDOWN:
            # Manual Arrow movements routing updates to C++ architecture logic via JSON
            if event.key == pygame.K_UP:
                Bridge.save_user_action("MOVE", {"dir": "UP"})
                active_log_message = "Manual action: Move UP"
            elif event.key == pygame.K_DOWN:
                Bridge.save_user_action("MOVE", {"dir": "DOWN"})
                active_log_message = "Manual action: Move DOWN"
            elif event.key == pygame.K_LEFT:
                Bridge.save_user_action("MOVE", {"dir": "LEFT"})
                active_log_message = "Manual action: Move LEFT"
            elif event.key == pygame.K_RIGHT:
                Bridge.save_user_action("MOVE", {"dir": "RIGHT"})
                active_log_message = "Manual action: Move RIGHT"
                
            # Key 'G': Executes Greedy Optimization Method Search
            elif event.key == pygame.K_g:
                best_item = find_best_treasure_greedy(
                    player_pos=current_game_state["player_pos"],
                    treasure_list=current_game_state["treasures"]
                )
                if best_item:
                    active_log_message = f"Greedy found: {best_item['name']}"
                    Bridge.save_user_action("RUN_GREEDY", {
                        "target_name": best_item["name"],
                        "target_x": best_item["x"],
                        "target_y": best_item["y"],
                        "value": best_item["value"]
                    })
                else:
                    active_log_message = "Greedy: No items left"
                    
            # Key 'B': Executes Depth-Limited State Space Backtracking Search
            elif event.key == pygame.K_b:
                remaining_backtracking = current_game_state.get("backtracking_remaining", BACKTRACKING_MAX_USES)
                if remaining_backtracking <= 0:
                    active_log_message = "No backtracking uses left."
                else:
                    step_budget_limit = 10  # Evaluates best paths up to 10 moves deep
                    search_result = plan_path_backtracking(
                        start_pos=current_game_state["player_pos"],
                        step_limit=step_budget_limit,
                        item_list=current_game_state["treasures"]
                    )
                    
                    calculated_route = search_result["calculated_path"]
                    
                    if len(calculated_route) > 1:
                        active_log_message = f"BT planned: {len(calculated_route)-1} steps"
                        Bridge.save_user_action("RUN_BACKTRACKING", {
                            "planned_path": calculated_route,
                            "total_steps": len(calculated_route) - 1,
                            "projected_yield": search_result["total_yield"]
                        })
                    else:
                        active_log_message = "BT: No efficient path found"

    # Swap visual pipeline memory frames
    pygame.display.flip()
    frame_clock.tick(30)  # Lock render throughput speed cap to 30 FPS

# Tear down subsystem contexts upon game loop interruption
pygame.quit()
sys.exit()




