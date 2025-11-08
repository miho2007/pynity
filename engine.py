import importlib
from scene_data import scene_data
import pygame
import time
import os

# --- Load scripts for all objects ---
for obj in scene_data:
    if "scripts" in obj:
        obj["modules"] = []
        for script_name in obj["scripts"]:
            try:
                module = importlib.import_module(script_name)
                obj["modules"].append(module)
            except ModuleNotFoundError:
                print(f"Script '{script_name}' not found!")

# --- Initialize Pygame ---
pygame.init()
screen = pygame.display.set_mode((1000, 500))
clock = pygame.time.Clock()

# --- Load images ---
for obj in scene_data:
    if obj["type"] == "image":
        if os.path.exists(obj["image_path"]):
            img = pygame.image.load(obj["image_path"]).convert_alpha()
            obj["image_obj"] = pygame.transform.scale(img, (int(obj["width"]), int(obj["height"])))
        else:
            print(f"Image not found: {obj['image_path']}")

last_time = time.time()
running = True
while running:
    dt = time.time() - last_time
    last_time = time.time()

    # --- Event handling ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # --- Update objects using all assigned scripts ---
    for obj in scene_data:
        if "modules" in obj:
            for module in obj["modules"]:
                try:
                    module.update(obj, dt)
                except Exception as e:
                    print(f"Script {module.__name__} update() error: {e}")

    # --- Draw everything ---
    screen.fill((30, 30, 30))  # background

    for obj in scene_data:
        if obj["type"] == "rect":
            pygame.draw.rect(screen, obj["color"], pygame.Rect(obj["x"], obj["y"], obj["width"], obj["height"]))
        elif obj["type"] == "image" and "image_obj" in obj:
            screen.blit(obj["image_obj"], (obj["x"], obj["y"]))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
