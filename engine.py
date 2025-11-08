import importlib
from scene_data import scene_data
import pygame
import time
import os

# --- Load scripts ---
for obj in scene_data:
    if "script" in obj and obj["script"]:
        obj["module"] = importlib.import_module(obj["script"])

# --- Initialize Pygame ---
pygame.init()
screen = pygame.display.set_mode((1000, 500))
clock = pygame.time.Clock()

# --- Load images ---
for obj in scene_data:
    if obj["type"] == "image" and "image_path" in obj and obj["image_path"]:
        if os.path.exists(obj["image_path"]):
            img = pygame.image.load(obj["image_path"]).convert_alpha()
            obj["pygame_image"] = img
        else:
            print(f"Warning: Image '{obj['image_path']}' not found")
            obj["pygame_image"] = None

last_time = time.time()
running = True
while running:
    dt = time.time() - last_time  # time delta
    last_time = time.time()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # --- Update objects using scripts ---
    for obj in scene_data:
        if "module" in obj:
            obj["module"].update(obj, dt)  # call exactly as before

    # --- Draw ---
    screen.fill((30, 30, 30))  # background

    for obj in scene_data:
        if obj["type"] == "rect":
            pygame.draw.rect(screen, obj["color"], pygame.Rect(obj["x"], obj["y"], obj["width"], obj["height"]))
        elif obj["type"] == "image" and "pygame_image" in obj and obj["pygame_image"]:
            screen.blit(obj["pygame_image"], (obj["x"], obj["y"]))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
