import importlib
import pygame
import time
from scene_data import scene_data  # exported from your editor

# --- Load scripts for objects ---
for obj in scene_data:
    if "script" in obj and obj["script"]:
        try:
            obj["module"] = importlib.import_module(obj["script"])
        except ModuleNotFoundError:
            print(f"Warning: Script '{obj['script']}' not found for object {obj.get('id', obj)}.")

# --- Initialize Pygame ---
pygame.init()
screen = pygame.display.set_mode((1000, 500))
pygame.display.set_caption("Pynity Engine Preview")
clock = pygame.time.Clock()

last_time = time.time()
running = True
while running:
    # --- Calculate delta time ---
    dt = time.time() - last_time
    last_time = time.time()

    # --- Handle events ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # --- Gather input state for scripts ---
    keys = pygame.key.get_pressed()
    input_state = {
        "up": keys[pygame.K_w],
        "down": keys[pygame.K_s],
        "left": keys[pygame.K_a],
        "right": keys[pygame.K_d]
    }

    # --- Update objects using scripts ---
    for obj in scene_data:
        if "module" in obj:
            obj["module"].update(obj, input_state, dt)

    # --- Draw objects ---
    screen.fill((30, 30, 30))  # background color
    for obj in scene_data:
        if obj["type"] == "rect":
            pygame.draw.rect(
                screen,
                obj["color"],
                pygame.Rect(obj["x"], obj["y"], obj["width"], obj["height"])
            )

    pygame.display.flip()
    clock.tick(60)  # cap FPS

pygame.quit()
