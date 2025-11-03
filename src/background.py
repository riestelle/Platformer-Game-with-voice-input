import pygame, os
from settings import WIDTH, HEIGHT

ASSET_DIR = os.path.join(os.path.dirname(__file__), "../assets")

class ParallaxBackground:
    def __init__(self):
        BG_PATH = os.path.join(ASSET_DIR, "bg")
        self.layers = [
            pygame.image.load(os.path.join(BG_PATH, "bg1.png")).convert(),
            # pygame.image.load(os.path.join(BG_PATH, "bg2.png")).convert_alpha(),
            # pygame.image.load(os.path.join(BG_PATH, "bg3.png")).convert_alpha(),
            # pygame.image.load(os.path.join(BG_PATH, "bg4.png")).convert_alpha(),
        ]
        self.speeds = [0.2, 0.4, 0.6, 0.8]

        for i in range(len(self.layers)):
            h = self.layers[i].get_height()
            scale = HEIGHT / h
            w = int(self.layers[i].get_width() * scale)
            self.layers[i] = pygame.transform.scale(self.layers[i], (w, HEIGHT))

    def draw(self, surface, camera):
        cam_x = camera.x if hasattr(camera, "x") else camera
        for i, layer in enumerate(self.layers):
            speed = self.speeds[i]
            layer_w = layer.get_width()
            x = -cam_x * speed % layer_w  

            surface.blit(layer, (x - layer_w, 0))
            surface.blit(layer, (x, 0))
