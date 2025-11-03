import pygame
from typing import List, Optional
from settings import TILE_SIZE, ENEMY_COLOR


class Enemy(pygame.sprite.Sprite):


    def __init__(
        self,
        x: int,
        y: int,
        patrol_width: int = 3,
        speed: float = 1.6,
        sprite_paths: Optional[list[str]] = None,
    ):
        super().__init__()

        self.frames = []
        if sprite_paths:
            for path in sprite_paths:
                try:
                    img = pygame.image.load(path).convert_alpha()
                    scaled_size = (int(TILE_SIZE * 0.75), int(TILE_SIZE * 0.75))
                    img = pygame.transform.smoothscale(img, scaled_size)
                    self.frames.append(img)
                except Exception as e:
                    print(f"[Enemy] Failed to load sprite {path}: {e}")
        if not self.frames:
            self.frames = [self._make_fallback_surface()]

        self.image = self.frames[0]
        self.rect = self.image.get_rect(midbottom=(x + TILE_SIZE // 2, y + TILE_SIZE))

        self.rect.y += TILE_SIZE // 8

        self.pos_x = float(self.rect.x)
        self.pos_y = float(self.rect.y)
        self.origin_x = x
        self.patrol_width = max(0, patrol_width) * TILE_SIZE
        self.speed = float(speed)
        self.vx = self.speed

        self.frame_index = 0
        self.animation_timer = 0.0
        self.animation_speed = 0.15  

        self.alive = True
        self.direction = 1 if self.vx >= 0 else -1

    def _make_fallback_surface(self):
        """Create a smaller, centered colored box for enemies."""
        size = int(TILE_SIZE * 0.75)
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.rect(surf, ENEMY_COLOR, surf.get_rect(), border_radius=6)
        return surf

    def update(self, colliders: List[pygame.Rect], dt: float):
        if not self.alive:
            return

        self.animation_timer += dt
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0.0
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            self.image = self.frames[self.frame_index]

        if self.direction < 0:
            self.image = pygame.transform.flip(self.frames[self.frame_index], True, False)
        else:
            self.image = self.frames[self.frame_index]

        move_x = self.vx * dt * 60.0
        self.pos_x += move_x
        self.rect.x = int(self.pos_x)

        if self.patrol_width > 0:
            if self.rect.x < self.origin_x:
                self.rect.x = self.origin_x
                self.pos_x = self.rect.x
                self.vx = abs(self.vx)
                self.direction = 1
            elif self.rect.x > self.origin_x + self.patrol_width:
                self.rect.x = self.origin_x + self.patrol_width
                self.pos_x = self.rect.x
                self.vx = -abs(self.vx)
                self.direction = -1

        for t in colliders:
            if self.rect.colliderect(t):
                if move_x > 0:
                    self.rect.right = t.left
                elif move_x < 0:
                    self.rect.left = t.right
                self.pos_x = self.rect.x
                self.vx = -self.vx
                self.direction = -self.direction
                break

    def draw(self, surface: pygame.Surface, camera):
        if not self.alive:
            return
        draw_pos = (
            self.rect.x - getattr(camera, "x", 0),
            self.rect.y - getattr(camera, "y", 0),
        )
        surface.blit(self.image, draw_pos)

    def kill(self):
        self.alive = False

    def reset_position(self):
        self.pos_x = float(self.origin_x)
        self.rect.x = int(self.pos_x)
        self.alive = True
        self.vx = abs(self.vx)
        self.direction = 1
