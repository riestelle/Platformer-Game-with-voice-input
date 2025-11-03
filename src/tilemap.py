# src/tilemap.py
"""
TileMap loader / renderer for simple ASCII tile maps with particle-based checkpoints.
"""
from pathlib import Path
import pygame
from typing import List, Tuple, Optional, Dict
from settings import TILE_SIZE, TILE_COLOR, SPIKE_COLOR, COIN_COLOR
from particle import CheckpointParticles

TILE_CHARS = {
    "X": "solid",
    "C": "coin",
    "S": "spike",
    "E": "enemy_spawn",
    "P": "checkpoint",
    "G": "goal",
    ".": None,
}

TileCoord = Tuple[int, int]
TileEntry = Tuple[int, int, str]


class TileMap:
    def __init__(self, filename: str):
        self.tiles: List[TileEntry] = []
        self.width = 0
        self.height = 0
        self.checkpoint_effects: List[CheckpointParticles] = []
        self._load_from_file(filename)

    def _load_from_file(self, filename: str):
        path = Path(filename)
        if not path.exists():
            raise FileNotFoundError(f"TileMap file not found: {filename}")
        with path.open("r", encoding="utf8") as f:
            lines = [ln.rstrip("\n") for ln in f if ln.strip("\n") != ""]
        self.width = max((len(r) for r in lines), default=0)
        self.height = len(lines)
        self.tiles.clear()
        for y, row in enumerate(lines):
            for x, ch in enumerate(row.ljust(self.width, ".")):
                self.tiles.append((x, y, ch))

        self.checkpoint_effects = [
            CheckpointParticles(tx, ty) for tx, ty in self.checkpoints()
        ]

    #  Tile helpers 
    def tile_to_world(self, tx: int, ty: int) -> Tuple[int, int]:
        return tx * TILE_SIZE, ty * TILE_SIZE

    def world_to_tile(self, px: int, py: int) -> Tuple[int, int]:
        return px // TILE_SIZE, py // TILE_SIZE

    def tile_rect(self, tx: int, ty: int) -> pygame.Rect:
        px, py = self.tile_to_world(tx, ty)
        return pygame.Rect(px, py, TILE_SIZE, TILE_SIZE)

    def coll_tiles(self) -> List[pygame.Rect]:
        return [
            pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            for x, y, ch in self.tiles if ch == "X"
        ]

    def coins(self) -> List[TileCoord]:
        return [(x, y) for x, y, ch in self.tiles if ch == "C"]

    def spikes(self) -> List[TileCoord]:
        return [(x, y) for x, y, ch in self.tiles if ch == "S"]

    def enemy_spawns(self) -> List[TileCoord]:
        return [(x, y) for x, y, ch in self.tiles if ch == "E"]

    def checkpoints(self) -> List[TileCoord]:
        return [(x, y) for x, y, ch in self.tiles if ch == "P"]

    def exits(self) -> List[TileCoord]:
        return [(x, y) for x, y, ch in self.tiles if ch == "G"]

    def tile_at(self, tx: int, ty: int) -> Optional[str]:
        for x, y, ch in self.tiles:
            if x == tx and y == ty:
                return ch
        return None

    def remove_tile(self, tx: int, ty: int, ch: Optional[str] = None) -> bool:
        for i, (x, y, c) in enumerate(self.tiles):
            if x == tx and y == ty and (ch is None or c == ch):
                self.tiles.pop(i)
                return True
        return False

    def collect_coin_at_world(self, px: int, py: int) -> bool:
        tx, ty = self.world_to_tile(px, py)
        return self.remove_tile(tx, ty, "C")

    #  Drawing 
    def draw(
        self,
        surface: pygame.Surface,
        camera: pygame.math.Vector2,
        tileset_images: Optional[Dict[str, pygame.Surface]] = None,
        active_checkpoints: Optional[List[TileCoord]] = None,
        dt: float = 0.016,
    ):
        use_images = bool(tileset_images)
        active_checkpoints = active_checkpoints or []

        for x, y, ch in self.tiles:
            if ch == ".":
                continue

            px = x * TILE_SIZE - camera.x
            py = y * TILE_SIZE - camera.y
            rect = pygame.Rect(px, py, TILE_SIZE, TILE_SIZE)

            if ch == "X":
                if use_images and tileset_images.get("X"):
                    surf = tileset_images["X"]
                    if surf.get_width() != TILE_SIZE or surf.get_height() != TILE_SIZE:
                        surf = pygame.transform.scale(surf, (TILE_SIZE, TILE_SIZE))
                    surface.blit(surf, rect.topleft)
                else:
                    pygame.draw.rect(surface, TILE_COLOR, rect)
                    inner = rect.inflate(-max(4, TILE_SIZE // 6), -max(4, TILE_SIZE // 6))
                    brighter = tuple(min(255, c + 20) for c in TILE_COLOR)
                    pygame.draw.rect(surface, brighter, inner)

            elif ch == "C":
                if use_images and tileset_images.get("C"):
                    surf = tileset_images["C"]
                    if surf.get_width() != TILE_SIZE or surf.get_height() != TILE_SIZE:
                        surf = pygame.transform.scale(surf, (TILE_SIZE, TILE_SIZE))
                    surface.blit(surf, rect.topleft)
                else:
                    pygame.draw.circle(surface, COIN_COLOR, rect.center, TILE_SIZE // 3)

            elif ch == "S":
                if use_images and tileset_images.get("S"):
                    surf = tileset_images["S"]
                    if surf.get_width() != TILE_SIZE or surf.get_height() != TILE_SIZE:
                        surf = pygame.transform.scale(surf, (TILE_SIZE, TILE_SIZE))
                    surface.blit(surf, rect.topleft)
                else:
                    pts = [(px, py + TILE_SIZE), (px + TILE_SIZE / 2, py + 6), (px + TILE_SIZE, py + TILE_SIZE)]
                    pygame.draw.polygon(surface, SPIKE_COLOR, pts)

            elif ch == "P":
                continue  # handled by particles

            elif ch == "G":
                pygame.draw.rect(surface, (180, 140, 255), rect.inflate(-8, -8), border_radius=6)
                pygame.draw.rect(surface, (240, 220, 255), rect.inflate(-20, -20), border_radius=4)

        for effect in self.checkpoint_effects:
            effect.active = (effect.tx, effect.ty) in active_checkpoints
            effect.update(dt)
            effect.draw(surface, camera)

    # Debug 
    def debug_print(self):
        rows = [["." for _ in range(self.width)] for _ in range(self.height)]
        for x, y, ch in self.tiles:
            if 0 <= y < self.height and 0 <= x < self.width:
                rows[y][x] = ch
        print("\n".join("".join(r) for r in rows))
