"""
DISTRITAL FRANCISCO JOSÉ DE CALDAS UNIVERSITY
COURSE: COMPUTER SCIENCES I (2026-I)

PROJECT: TREASURE HUNT
COMPONENT: INTERACTIVE PYGAME USER INTERFACE
"""

import os
import sys
import pygame

# Dynamic path configuration to allow importing components located on parent directories
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import Bridge  

# Initialize the framework context
pygame.init()

# Viewport dimensions & spatial constants (Constraint: Minimum 8x8 setup)
CELL_SIZE = 60
GRID_SIZE = 8
HUD_WIDTH = 240
WINDOW_WIDTH = (GRID_SIZE * CELL_SIZE) + HUD_WIDTH
WINDOW_HEIGHT = GRID_SIZE * CELL_SIZE

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Treasure Hunt Simulation - Engine Interface")
frame_tracker = pygame.time.Clock()

# Strict UI color palette declarations
COLOR_BG = (24, 24, 27)
COLOR_GRID = (39, 39, 42)
COLOR_PLAYER = (59, 130, 246)
COLOR_TREASURE = (234, 179, 8)
COLOR_TEXT = (244, 244, 245)

def render_matrix_grid():
    """Draws the primary interactive cell coordinates layout."""
    for x in range(0, GRID_SIZE * CELL_SIZE, CELL_SIZE):
        for y in range(0, GRID_SIZE * CELL_SIZE, CELL_SIZE):
            cell_rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, COLOR_GRID, cell_rect, 1)

def render_sidebar_hud(game_state):
    """Draws contextual simulation logs and player data indicators."""
    font_body = pygame.font.SysFont("Arial", 16)
    font_header = pygame.font.SysFont("Arial", 18, bold=True)
    
    # Draw HUD background box
    panel_rect = pygame.Rect(GRID_SIZE * CELL_SIZE, 0, HUD_WIDTH, WINDOW_HEIGHT)
    pygame.draw.rect(screen, (39, 39, 42), panel_rect)
    
    # Render operational variables
    header_surface = font_header.render("TREASURE HUNT", True, COLOR_TREASURE)
    screen.blit(header_surface, (GRID_SIZE * CELL_SIZE + 20, 20))
    
    pos_surface = font_body.render(f"Coordinates: {game_state['player_pos']}", True, COLOR_TEXT)
    screen.blit(pos_surface, (GRID_SIZE * CELL_SIZE + 20, 60))
    
    score_surface = font_body.render(f"Total Score: {game_state['score']}", True, COLOR_TEXT)
    screen.blit(score_surface, (GRID_SIZE * CELL_SIZE + 20, 90))

# Initialize Application Execution Loop
application_running = True
while application_running:
    screen.fill(COLOR_BG)
    render_matrix_grid()
    
    # 1. Pull data updates from the interface data Bridge
    active_state = Bridge.read_game_state()
    
    # 2. Render entity objects parsed from structural representations
    # Draw active treasure coordinates
    for item in active_state["treasures"]:
        tx, ty = item["x"], item["y"]
        item_bounds = pygame.Rect(tx * CELL_SIZE + 15, ty * CELL_SIZE + 15, CELL_SIZE - 30, CELL_SIZE - 30)
        pygame.draw.ellipse(screen, COLOR_TREASURE, item_bounds)
        
    # Draw player node position
    px, py = active_state["player_pos"]
    agent_bounds = pygame.Rect(px * CELL_SIZE + 10, py * CELL_SIZE + 10, CELL_SIZE - 20, CELL_SIZE - 20)
    pygame.draw.rect(screen, COLOR_PLAYER, agent_bounds)
    
    # Render auxiliary metadata interface
    render_sidebar_hud(active_state)
    
    # 3. Intercept user events and execute tracking actions
    for user_event in pygame.event.get():
        if user_event.type == pygame.QUIT:
            application_running = False
            
        elif user_event.type == pygame.KEYDOWN:
            if user_event.key == pygame.K_UP:
                Bridge.save_user_action("MOVE", {"dir": "UP"})
            elif user_event.key == pygame.K_DOWN:
                Bridge.save_user_action("MOVE", {"dir": "DOWN"})
            elif user_event.key == pygame.K_LEFT:
                Bridge.save_user_action("MOVE", {"dir": "LEFT"})
            elif user_event.key == pygame.K_RIGHT:
                Bridge.save_user_action("MOVE", {"dir": "RIGHT"})
            elif user_event.key == pygame.K_g:
                Bridge.save_user_action("RUN_GREEDY")
            elif user_event.key == pygame.K_b:
                Bridge.save_user_action("RUN_BACKTRACKING", {"step_limit": 10})

    pygame.display.flip()
    frame_tracker.tick(30) # Anchor processing speeds to 30 frames per second

pygame.quit()
sys.exit()