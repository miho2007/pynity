import pygame

def update(obj, dt):
    keys = pygame.key.get_pressed()
    speed = 200  # pixels per second

    if keys[pygame.K_w]:
        obj["y"] -= speed * dt
    if keys[pygame.K_s]:
        obj["y"] += speed * dt
    if keys[pygame.K_a]:
        obj["x"] -= speed * dt
    if keys[pygame.K_d]:
        obj["x"] += speed * dt
