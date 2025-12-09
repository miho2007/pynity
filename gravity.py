# gravity.py
GRAVITY = 500  # pixels per second squared

def update(obj, dt):
    if "collider" not in obj:
        return

    # Initialize vertical velocity if not exists
    if "vy" not in obj:
        obj["vy"] = 0

    # Apply gravity
    obj["vy"] += GRAVITY * dt
    new_y = obj["y"] + obj["vy"] * dt

    # Temporarily move object
    old_y = obj["y"]
    obj["y"] = new_y
    obj["collider"].update_mask()

    # Check collisions against all other objects
    from engine import scene_data  # import current scene
    for other in scene_data:
        if other is obj or "collider" not in other:
            continue
        if obj["collider"].check_collision(other["collider"]):
            # Undo movement and stop falling
            obj["y"] = old_y
            obj["vy"] = 0
            break
