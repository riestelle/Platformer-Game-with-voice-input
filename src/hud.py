import pygame
import math
from settings import HUD_COLOR, COIN_COLOR  


class HUD:
    def __init__(self, font):
        self.font = font
        self.last_score = 0
        self.last_coins = 0
        self.last_lives = 0
        self.last_level = 1
        self.checkpoint_timer = 0
        self.checkpoint_duration = 2000  

    def trigger_checkpoint(self):
        #Call this when player reaches a checkpoint
        self.checkpoint_timer = self.checkpoint_duration

    def update(self, dt):
        if self.checkpoint_timer > 0:
            self.checkpoint_timer = max(0, self.checkpoint_timer - dt)

    def draw(self, surface, score, lives, coins, level_number=1):
        base_y = 10
        t = pygame.time.get_ticks() * 0.005

        def draw_text_with_shadow(text, x, y, color, shadow=(0, 0, 0)):
            shadow_surf = self.font.render(text, True, shadow)
            surface.blit(shadow_surf, (x + 2, y + 2))
            text_surf = self.font.render(text, True, color)
            surface.blit(text_surf, (x, y))

        #  Animated scales if something changes 
        score_scale = 1.0 + 0.1 * math.sin(t) if score != self.last_score else 1.0
        coin_scale = 1.0 + 0.1 * math.sin(t) if coins != self.last_coins else 1.0
        life_scale = 1.0 + 0.1 * math.sin(t) if lives != self.last_lives else 1.0
        level_scale = 1.0 + 0.1 * math.sin(t) if level_number != self.last_level else 1.0

        # Scaled fonts
        score_font = pygame.font.Font(None, int(self.font.get_height() * score_scale))
        coin_font = pygame.font.Font(None, int(self.font.get_height() * coin_scale))
        life_font = pygame.font.Font(None, int(self.font.get_height() * life_scale))
        level_font = pygame.font.Font(None, int(self.font.get_height() * level_scale))

        #  Draw the HUD elements 
        draw_text_with_shadow(f"Score: {score}", 10, base_y, HUD_COLOR)
        draw_text_with_shadow(f"Lives: {lives}", 180, base_y, HUD_COLOR)
        draw_text_with_shadow(f"Coins: {coins}", 310, base_y, COIN_COLOR)
        draw_text_with_shadow(f"Level: {level_number}", 450, base_y, (180, 255, 180))

        #  Checkpoint message glow 
        if self.checkpoint_timer > 0:
            alpha = int(255 * (self.checkpoint_timer / self.checkpoint_duration))
            alpha = max(0, min(255, alpha))

            big_font = pygame.font.Font(None, 50)  
            text = "Checkpoint reached!"

            text_shadow = big_font.render(text, True, (50, 50, 50))
            text_surface = big_font.render(text, True, (255, 255, 255))

            text_surface.set_alpha(alpha)
            text_shadow.set_alpha(alpha)

            center_x = surface.get_width() // 2
            y = 70  

            surface.blit(text_shadow, text_shadow.get_rect(center=(center_x + 3, y + 3)))
            surface.blit(text_surface, text_surface.get_rect(center=(center_x, y)))

        self.last_score = score
        self.last_coins = coins
        self.last_lives = lives
        self.last_level = level_number
