# movement.py
import pygame

# Speed in pixels per second
SPEED = 200

# Optional: list of objects to check collisions against
other_objects = []

def update(obj, dt):
    keys = pygame.key.get_pressed()
    dx = 0
    dy = 0

    if keys[pygame.K_w]:
        dy = -SPEED * dt
    if keys[pygame.K_s]:
        dy = SPEED * dt
    if keys[pygame.K_a]:
        dx = -SPEED * dt
    if keys[pygame.K_d]:
        dx = SPEED * dt

    # Move object tentatively
    obj["x"] += dx
    obj["y"] += dy

    # Update collider after movement
    if "collider" in obj:
        obj["collider"].update_mask()

    # Check collisions
    for other in other_objects:
        if other is obj or "collider" not in other:
            continue
        if obj["collider"].check_collision(other["collider"]):
            # Collision detected → revert movement
            obj["x"] -= dx
            obj["y"] -= dy
            obj["collider"].update_mask()
            print(f"{obj} collided with {other}")
            break
