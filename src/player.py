# player.py
import pygame, time
from settings import *
from math import copysign

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, sprites: dict = None):
        super().__init__()
        self.sprites = sprites or {}
        self._input_moving = False
        sprite_surf = self.sprites.get("idle")
        if sprite_surf:
            self.image = sprite_surf
            w, h = self.image.get_size()  
            self.rect = pygame.Rect(int(x) + 4, int(y) + 4, w, h)
        else:
            surf = pygame.Surface((TILE_SIZE-8, TILE_SIZE-8), pygame.SRCALPHA)
            pygame.draw.rect(surf, (80,200,240), surf.get_rect(), border_radius=6)
            self.image = surf
            self.rect = self.image.get_rect(topleft=(int(x)+4, int(y)+4))
        self.anim_timer = 0.0
        self.anim_frame = 0
        self.walk_frame_time = 0.15  

        self._move_start_thresh = 0.6
        self._move_stop_thresh  = 0.3
        self._was_moving = False

        self.vx = 0.0
        self.vy = 0.0
        self.on_ground = False
        self.facing_right = True
        self.invulnerable = 0

        self._last_ground_time = -999.0
        self._jump_pressed_time = -999.0

        self.can_double_jump = ALLOW_DOUBLE_JUMP
        self.dash_available = ALLOW_DASH
        self._dashing = False
        self._dash_start = 0
        self._dash_dir = 0
        self._last_dash_time = -999.0

        self._touching_wall_left = False
        self._touching_wall_right = False

    def _get_default_image(self):
        return self.sprites.get("idle", self.image)

    def handle_input(self, keys):
        if self._dashing:
            self._input_moving = False
            return
        left = keys[pygame.K_LEFT] or keys[pygame.K_a]
        right = keys[pygame.K_RIGHT] or keys[pygame.K_d]

        if left and not right:
            self.vx = -PLAYER_SPEED
            self.facing_right = False
            self._input_moving = True
        elif right and not left:
            self.vx = PLAYER_SPEED
            self.facing_right = True
            self._input_moving = True
        else:
            self.vx = 0
            self._input_moving = False

        if keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP]:
            self._jump_pressed_time = pygame.time.get_ticks() / 1000.0

    def apply_physics(self):
        now_ms = pygame.time.get_ticks()
        if self._dashing:
            self.vy = 0
            self.vx = self._dash_dir * DASH_SPEED
            if now_ms - self._dash_start > DASH_DURATION_MS:
                self._dashing = False
                self._last_dash_time = now_ms
                self.vx = self._dash_dir * (DASH_SPEED * 0.35)
        else:
            self.vy += GRAVITY
            if self.vy > 30: self.vy = 30

    def try_dash(self, dir_x):
        if not ALLOW_DASH: return False
        now_ms = pygame.time.get_ticks()
        if self.dash_available and (now_ms - self._last_dash_time) > DASH_COOLDOWN_MS:
            self._dashing = True
            self._dash_start = now_ms
            self._dash_dir = copysign(1, dir_x) if dir_x != 0 else (1 if self.facing_right else -1)
            self.dash_available = False
            return True
        return False

    def try_consume_jump(self):
        now = pygame.time.get_ticks() / 1000.0
        since_ground = now - self._last_ground_time
        since_jump = now - self._jump_pressed_time

        if ALLOW_WALL_JUMP and not self.on_ground:
            if self._touching_wall_left and since_jump <= JUMP_BUFFER_TIME:
                self.vy = JUMP_VELOCITY
                self.vx = PLAYER_SPEED * 1.25
                self._jump_pressed_time = -999.0
                return True
            if self._touching_wall_right and since_jump <= JUMP_BUFFER_TIME:
                self.vy = JUMP_VELOCITY
                self.vx = -PLAYER_SPEED * 1.25
                self._jump_pressed_time = -999.0
                return True

        if since_jump <= JUMP_BUFFER_TIME and since_ground <= COYOTE_TIME:
            self.vy = JUMP_VELOCITY
            self._jump_pressed_time = -999.0
            self._last_ground_time = -999.0
            self.on_ground = False
            self.can_double_jump = ALLOW_DOUBLE_JUMP
            return True

        if ALLOW_DOUBLE_JUMP and self.can_double_jump and since_jump <= JUMP_BUFFER_TIME:
            self.vy = JUMP_VELOCITY * 0.88
            self.vx += (PLAYER_SPEED * (0.5 if self.facing_right else -0.5))
            self.can_double_jump = False
            self._jump_pressed_time = -999.0
            return True

        return False

    def update(self, colliders, dt):
        self._touching_wall_left = False
        self._touching_wall_right = False

        self.rect.x += int(self.vx)
        for t in colliders:
            if self.rect.colliderect(t):
                if self.vx > 0:
                    self.rect.right = t.left
                    self.vx = 0
                    self._touching_wall_right = True
                elif self.vx < 0:
                    self.rect.left = t.right
                    self.vx = 0
                    self._touching_wall_left = True

        self.rect.y += int(self.vy)
        self.on_ground = False
        for t in colliders:
            if self.rect.colliderect(t):
                if self.vy > 0:
                    self.rect.bottom = t.top
                    self.vy = 0
                    self.on_ground = True
                    self._last_ground_time = pygame.time.get_ticks() / 1000.0
                    self.dash_available = ALLOW_DASH
                    self.can_double_jump = ALLOW_DOUBLE_JUMP
                elif self.vy < 0:
                    self.rect.top = t.bottom
                    self.vy = 0

        self.try_consume_jump()

        if (not getattr(self, "_input_moving", False)) and self.on_ground and abs(self.vx) < 0.2:
            self.anim_timer = 0.0
            self.anim_frame = 0
            self._was_moving = False
            self._effective_moving = False
            self.vx = 0.0
            if getattr(self, "invulnerable", 0) > 0:
                self.invulnerable -= 1
            return

        if abs(self.vx) < 0.15:
            self.vx = 0.0

        if getattr(self, "_input_moving", False):
            moving = True
        else:
            start_t = getattr(self, "_move_start_thresh", 0.6)
            stop_t  = getattr(self, "_move_stop_thresh", 0.3)
            if abs(self.vx) > start_t:
                moving = True
            elif abs(self.vx) < stop_t:
                moving = False
            else:
                moving = getattr(self, "_was_moving", False)

        if not moving and getattr(self, "_was_moving", False):
            self._stable_timer = getattr(self, "_stable_timer", 0.0) + dt
            stabilized = self._stable_timer >= getattr(self, "_stable_delay", 0.08)
        else:
            self._stable_timer = 0.0
            stabilized = True

        effective_moving = moving if moving else (not getattr(self, "_was_moving", False) or stabilized)

        if effective_moving:
            self.anim_timer = getattr(self, "anim_timer", 0.0) + dt
            if self.anim_timer >= getattr(self, "walk_frame_time", 0.15):
                self.anim_timer -= getattr(self, "walk_frame_time", 0.15)
                self.anim_frame = (getattr(self, "anim_frame", 0) + 1) % 2
        else:
            self.anim_timer = 0.0
            self.anim_frame = 0

        self._was_moving = moving
        self._effective_moving = effective_moving

        if getattr(self, "invulnerable", 0) > 0:
            self.invulnerable -= 1
            print(f"vx={self.vx:.2f} input={self._input_moving} moving={self._was_moving} eff={self._effective_moving} anim={self.anim_frame}")
    def pickup_dash_refill(self):
        self.dash_available = True

    def _choose_sprite(self):
        if not self.on_ground and abs(self.vy) > 1.0 and "jump" in self.sprites:
            return self.sprites["jump"]

        if self.on_ground and getattr(self, "_effective_moving", False):
            return self.sprites.get("walk1") if self.anim_frame == 0 else self.sprites.get("walk2")
        return self.sprites.get("idle", self.image)



    def draw(self, surface, camera):
        img = self._choose_sprite()

        if not self.facing_right:
            img = pygame.transform.flip(img, True, False)

        draw_pos = (int(self.rect.x - camera.x), int(self.rect.y - camera.y))

        if getattr(self, "invulnerable", 0) > 0:
            if self.invulnerable % 10 < 5:
                surface.blit(img, draw_pos)
        else:
            surface.blit(img, draw_pos)

def find_safe_spawn(tm, fallback=(100, 100)):
    """
    Scan the tilemap for a safe spawn location.
    Prefers solid ground with air above, avoids spikes and edges.
    """
    safe_spots = []
    ground_tiles = tm.coll_tiles()
    spike_coords = set(tm.spikes())

    for y in range(tm.height - 2, 1, -1):  
        for x in range(1, tm.width - 1):   
            here = tm.tile_at(x, y)
            below = tm.tile_at(x, y + 1)
            above1 = tm.tile_at(x, y - 1)
            above2 = tm.tile_at(x, y - 2)

            if below == 'X' and here == '.' and above1 == '.' and above2 == '.':
                nearby_spike = any(abs(sx - x) <= 1 and abs(sy - y) <= 1 for sx, sy in spike_coords)
                if nearby_spike:
                    continue
                safe_spots.append((x, y))
    if safe_spots:
        mid_x = tm.width // 2
        safe_spots.sort(key=lambda p: (abs(p[0] - mid_x), -p[1])) 
        x, y = safe_spots[0]
        return x * TILE_SIZE, y * TILE_SIZE

    print("[spawn] No valid ground found, using fallback:", fallback)
    return fallback


