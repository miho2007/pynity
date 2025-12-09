import pygame

class Collider:
    def __init__(self, obj):
        self.obj = obj
        # For images, create mask from image surface
        if "image_obj" in obj:
            self.mask = pygame.mask.from_surface(obj["image_obj"])
            self.rect = obj["image_obj"].get_rect(topleft=(obj["x"], obj["y"]))
        else:
            # For rectangles, create a surface for mask
            self.surface = pygame.Surface((obj["width"], obj["height"]))
            self.surface.fill((255, 255, 255))
            self.mask = pygame.mask.from_surface(self.surface)
            self.rect = pygame.Rect(obj["x"], obj["y"], obj["width"], obj["height"])

    def update_mask(self):
        # Update rect position
        self.rect.topleft = (self.obj["x"], self.obj["y"])
        # Regenerate mask if it's a rectangle
        if hasattr(self, "surface"):
            self.mask = pygame.mask.from_surface(self.surface)
        # For images, regenerate mask from image_obj
        elif "image_obj" in self.obj:
            self.mask = pygame.mask.from_surface(self.obj["image_obj"])

    def check_collision(self, other):
        if self.mask is None or other.mask is None:
            return False
        offset = (other.rect.x - self.rect.x, other.rect.y - self.rect.y)
        return self.mask.overlap(other.mask, offset) is not None
