# src/particle.py
import pygame
import random
from settings import TILE_SIZE
import math

class CheckpointParticles:
    """
    A circular aura + floating particles for checkpoints.
    """
    def __init__(self, tx, ty):
        self.tx = tx
        self.ty = ty
        self.x = tx * TILE_SIZE + TILE_SIZE // 2
        self.y = ty * TILE_SIZE + TILE_SIZE // 2
        self.radius = TILE_SIZE // 3
        self.particles = []
        self.timer = 0

    def update(self, dt):
        self.timer += dt

        for p in self.particles:
            p['y'] -= p['speed'] * dt
            p['life'] -= dt
        self.particles = [p for p in self.particles if p['life'] > 0]

        if random.random() < 0.2:
            angle = random.uniform(0, 2*math.pi)
            dist = random.uniform(0, self.radius)  
            px = self.x + math.cos(angle) * dist
            py = self.y + math.sin(angle) * dist
            self.particles.append({
                'x': px,
                'y': py,
                'radius': random.randint(1,2),
                'life': random.uniform(0.5,1.2),
                'speed': random.uniform(10, 30)
            })

    def draw(self, surface, camera):
        # Floating center aura
        aura_radius = self.radius + 2 + math.sin(self.timer*2)  # was +4 + sin*2
        pygame.draw.circle(surface, (100, 255, 255, 80), 
                           (int(self.x - camera.x), int(self.y - camera.y)), int(aura_radius), width=4)
        # Inner circle
        pygame.draw.circle(surface, (50,200,255), 
                           (int(self.x - camera.x), int(self.y - camera.y)), int(self.radius))
        # Draw particles
        for p in self.particles:
            pygame.draw.circle(surface, (200,255,255), 
                               (int(p['x'] - camera.x), int(p['y'] - camera.y)), p['radius'])
