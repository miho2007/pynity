import importlib
from scene_data import scene_data
import pygame
import time
import os

# --- Collider class supporting both images and rects ---
class Collider:
    def __init__(self, obj):
        self.obj = obj
        # Use mask if object has image, else create a mask for rect
        if "image_obj" in obj:
            self.mask = pygame.mask.from_surface(obj["image_obj"])
        else:
            surf = pygame.Surface((obj["width"], obj["height"]))
            surf.fill((255, 255, 255))
            self.mask = pygame.mask.from_surface(surf)
        self.rect = pygame.Rect(obj["x"], obj["y"], obj["width"], obj["height"])

    def update_mask(self):
        # Update rect position
        self.rect.topleft = (self.obj["x"], self.obj["y"])
        # Update mask if object has image
        if "image_obj" in self.obj:
            self.mask = pygame.mask.from_surface(self.obj["image_obj"])

    def check_collision(self, other):
        if self.mask and other.mask:
            offset = (other.rect.x - self.rect.x, other.rect.y - self.rect.y)
            return self.mask.overlap(other.mask, offset) is not None
        else:
            return self.rect.colliderect(other.rect)

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

# --- Load images and assign colliders ---
for obj in scene_data:
    if obj["type"] == "image":
        if os.path.exists(obj["image_path"]):
            img = pygame.image.load(obj["image_path"]).convert_alpha()
            obj["image_obj"] = pygame.transform.scale(img, (int(obj["width"]), int(obj["height"])))
        else:
            print(f"Image not found: {obj['image_path']}")
    # Automatically assign collider
    obj["collider"] = Collider(obj)

# --- Assign other_objects for movement scripts ---
for obj in scene_data:
    if "modules" in obj:
        for module in obj["modules"]:
            # Only assign other_objects if the script defines it
            if hasattr(module, "other_objects"):
                module.other_objects = [o for o in scene_data if o is not obj]

# --- Main loop ---
last_time = time.time()
running = True
while running:
    dt = time.time() - last_time
    last_time = time.time()

    # --- Event handling ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # --- Update objects using assigned scripts ---
    for obj in scene_data:
        if "modules" in obj:
            for module in obj["modules"]:
                try:
                    if hasattr(module, "update"):
                        module.update(obj, dt)
                except Exception as e:
                    print(f"Script {module.__name__} update() error: {e}")

    # --- Update colliders ---
    for obj in scene_data:
        if "collider" in obj:
            obj["collider"].update_mask()

    # --- Check collisions ---
    for i, obj1 in enumerate(scene_data):
        for j, obj2 in enumerate(scene_data[i+1:], start=i+1):
            if "collider" in obj1 and "collider" in obj2:
                if obj1["collider"].check_collision(obj2["collider"]):
                    print(f"Collision detected between objects {i} and {j}!")

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
