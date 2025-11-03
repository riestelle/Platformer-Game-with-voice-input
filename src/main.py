# src/main.py
import pygame, sys, traceback, os
from pathlib import Path
from settings import *
from tilemap import TileMap
from player import Player
from enemy import Enemy
from hud import HUD
from menu import (
    show_main_menu,
    show_pause_menu,
    show_levels_menu,
    show_settings_menu,
    ensure_audio,
    save_audio_settings,
)
from audio import init_audio, play_music, play_sfx, stop_music, set_volumes
from settings import WIDTH, HEIGHT, FPS
from particle import CheckpointParticles as CheckpointEffect
from background import ParallaxBackground
from score_manager import save_score, get_score  
import menu

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("My Game")

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 28)
background = ParallaxBackground()

#  Paths 
base = Path(__file__).resolve().parent.parent
LEVEL_DIR = base / "levels"
ASSET_UI = os.path.join(str(base), "assets", "ui")
ASSET_SPRITES = os.path.join(str(base), "assets", "sprites")

#  Safe image loader 
def _safe_image(path: str):
    try:
        return pygame.image.load(path).convert_alpha()
    except Exception:
        return None

#  UI icons 
ICON_COIN  = _safe_image(os.path.join(ASSET_UI, "coin.png")) or _safe_image(os.path.join(str(base), "assets", "coin.png"))
ICON_SOLID = _safe_image(os.path.join(ASSET_UI, "solid.png")) or _safe_image(os.path.join(str(base), "assets", "solid.png"))
ICON_SPIKE = _safe_image(os.path.join(ASSET_UI, "spike.png")) or _safe_image(os.path.join(str(base), "assets", "spike.png"))

for name, surf in (("ICON_COIN", ICON_COIN), ("ICON_SOLID", ICON_SOLID), ("ICON_SPIKE", ICON_SPIKE)):
    if surf:
        try:
            globals()[name] = pygame.transform.scale(surf, (TILE_SIZE, TILE_SIZE))
        except Exception:
            globals()[name] = surf

#  Checkpoint images 
# CHECKPOINT_NOT_PRESSED = _safe_image("C:/Users/Kristelle/mygame/assets/checkpoint_button2.png")
# CHECKPOINT_PRESSED     = _safe_image("C:/Users/Kristelle/mygame/assets/checkpoint_button1.png")

#  Tileset dict 
TILESET_IMAGES = {}
if ICON_COIN:  TILESET_IMAGES['C'] = ICON_COIN
if ICON_SOLID: TILESET_IMAGES['X'] = ICON_SOLID
if ICON_SPIKE: TILESET_IMAGES['S'] = ICON_SPIKE
#if CHECKPOINT_NOT_PRESSED: TILESET_IMAGES['P'] = CHECKPOINT_NOT_PRESSED
if not TILESET_IMAGES:
    TILESET_IMAGES = None

#  Safe sprite loader 
def _safe_load(path):
    try:
        return pygame.image.load(path).convert_alpha()
    except Exception:
        return None

PLAYER_SPRITES = {
    "idle":  _safe_load(os.path.join(ASSET_SPRITES, "platformChar_idle.png")),
    "walk1": _safe_load(os.path.join(ASSET_SPRITES, "platformChar_walk1.png")),
    "walk2": _safe_load(os.path.join(ASSET_SPRITES, "platformChar_walk2.png")),
    "jump":  _safe_load(os.path.join(ASSET_SPRITES, "platformChar_jump.png")),
}
import os

#  Enemy Sprite Definitions 
ENEMY_SPRITES = {
    "spider": {
        "idle": [
            os.path.join(ASSET_SPRITES, "spider.png"),
        ],
        "walk": [
            os.path.join(ASSET_SPRITES, "spider_walk1.png"),
            os.path.join(ASSET_SPRITES, "spider_walk2.png"),
        ],
        "hit": [
            os.path.join(ASSET_SPRITES, "spider_hit.png"),
        ],
        "dead": [
            os.path.join(ASSET_SPRITES, "spider_dead.png"),
        ],
    },

    "bat": {
        "idle": [
            os.path.join(ASSET_SPRITES, "bat.png"),
            os.path.join(ASSET_SPRITES, "bat_hang.png"),
        ],
        "fly": [
            os.path.join(ASSET_SPRITES, "bat_fly.png"),
        ],
        "hit": [
            os.path.join(ASSET_SPRITES, "bat_hit.png"),
        ],
        "dead": [
            os.path.join(ASSET_SPRITES, "bat_dead.png"),
        ],
    },

    "spinner": {
        "idle": [
            os.path.join(ASSET_SPRITES, "spinner.png"),
        ],
        "spin": [
            os.path.join(ASSET_SPRITES, "spinner_spin.png"),
        ],
        "hit": [
            os.path.join(ASSET_SPRITES, "spinner_hit.png"),
        ],
        "dead": [
            os.path.join(ASSET_SPRITES, "spinner_dead.png"),
        ],
    },

    "spinnerHalf": {
        "idle": [
            os.path.join(ASSET_SPRITES, "spinnerHalf.png"),
        ],
        "spin": [
            os.path.join(ASSET_SPRITES, "spinnerHalf_spin.png"),
        ],
        "hit": [
            os.path.join(ASSET_SPRITES, "spinnerHalf_hit.png"),
        ],
        "dead": [
            os.path.join(ASSET_SPRITES, "spinnerHalf_dead.png"),
        ],
    },
}


PLAYER_W = TILE_SIZE
PLAYER_H = TILE_SIZE * 2  
for k, s in list(PLAYER_SPRITES.items()):
    if s:
        try:
            PLAYER_SPRITES[k] = pygame.transform.scale(s, (PLAYER_W, PLAYER_H))
        except Exception:
            PLAYER_SPRITES[k] = s

PLAYER_EDGE = TILE_SIZE - 8 
NORMAL_SIZE = (PLAYER_EDGE, PLAYER_EDGE)
for k, surf in list(PLAYER_SPRITES.items()):
    if surf:
        try:
            s = pygame.transform.smoothscale(surf, NORMAL_SIZE)
        except Exception:
            s = surf
        master = pygame.Surface(NORMAL_SIZE, pygame.SRCALPHA)
        w, h = s.get_size()
        ox = (NORMAL_SIZE[0] - w) // 2
        oy = (NORMAL_SIZE[1] - h) // 2
        master.blit(s, (ox, oy))
        PLAYER_SPRITES[k] = master
    else:
        PLAYER_SPRITES[k] = None

init_audio(music_vol=0.6, sfx_vol=0.9)
_audio = ensure_audio()
try:
    play_music("menu")
except Exception:
    pass

base = Path(__file__).resolve().parent.parent
LEVEL_DIR = base / "levels"

def discover_levels():
    try:
        return sorted([f for f in os.listdir(LEVEL_DIR) if f.endswith(".txt")])
    except Exception:
        return ["level1.txt","level2.txt","level3.txt"]

LEVEL_FILES = discover_levels()
current_level = 0

def level_path_for(idx):
    return LEVEL_DIR / LEVEL_FILES[idx]

if not level_path_for(0).exists():
    raise FileNotFoundError(f"Expected level file at: {level_path_for(0)}")

level_path = level_path_for(current_level)
tilemap = TileMap(str(level_path))
checkpoint_effects = [CheckpointEffect(tx, ty) for tx, ty in tilemap.checkpoints()]


def autosave_score(score):
    if not menu.current_user:
        print("[score] No user logged in, skipping autosave.")
        return
    try:
        save_score(menu.current_user, score)
        print(f"[score] Autosaved {score} pts for {menu.current_user}")
    except Exception as e:
        print("[score] Autosave failed:", e)


def find_safe_spawn(tm, fallback=(100, 100)):
    safe_x = 3  

    for y in range(tm.height - 2, 0, -1):
        here = tm.tile_at(safe_x, y)
        below = tm.tile_at(safe_x, y + 1)
        above = tm.tile_at(safe_x, y - 1)

        if below == 'X' and here == '.' and above == '.':
            spawn_x = safe_x * TILE_SIZE
            spawn_y = (y * TILE_SIZE) - TILE_SIZE // 2  
            print(f"[spawn] bottom-left safe spawn at ({spawn_x}, {spawn_y})")
            return spawn_x, spawn_y

    print("[spawn] No left ground found — using fallback.")
    return fallback



def start_of_level_spawn_three_in(tm, fallback=(100, 100)):
    for y in range(tm.height - 1, -1, -1):
        for x in range(tm.width):
            if tm.tile_at(x, y) == 'X' and tm.tile_at(x, y - 1) == '.':
                spawn_x = x * TILE_SIZE
                spawn_y = (y - 1) * TILE_SIZE
                return spawn_x, spawn_y
    return fallback


RESPAWN_POS = find_safe_spawn(tilemap, fallback=(100, 100))
FIXED_SPAWN_POS = RESPAWN_POS
player = Player(RESPAWN_POS[0], RESPAWN_POS[1], sprites=PLAYER_SPRITES)
hud = HUD(font, username=menu.current_user or "Guest")
user_score = get_score(menu.current_user) if menu.current_user else 0

def make_enemies_from_tilemap(tm):
    group = pygame.sprite.Group()

    types = ["spider", "bat", "spinner", "spinnerHalf"]

    type_settings = {
        "spider": {"y_offset": 0, "patrol_width": 3, "anim": "walk"},
        "bat": {"y_offset": -TILE_SIZE // 2, "patrol_width": 5, "anim": "fly"},
        "spinner": {"y_offset": -TILE_SIZE // 4, "patrol_width": 4, "anim": "spin"},
        "spinnerHalf": {"y_offset": -TILE_SIZE // 4, "patrol_width": 4, "anim": "spin"},
    }

    def has_solid_ground_below_range(tx, ty, patrol_tiles):
        """Return True if all tiles below patrol range are solid."""
        for dx in range(-patrol_tiles // 2, patrol_tiles // 2 + 1):
            if tm.tile_at(tx + dx, ty + 1) != "X":
                return False
        return True

    for i, (ex, ey) in enumerate(tm.enemy_spawns()):
        etype = types[i % len(types)]
        settings = type_settings.get(etype, type_settings["spider"])
        sprite_data = ENEMY_SPRITES.get(etype, {})
        sprite_paths = sprite_data.get(settings["anim"], [])

        below_tile = tm.tile_at(ex, ey + 1)
        above_tile = tm.tile_at(ex, ey - 1)
        patrol_tiles = settings["patrol_width"]

        if etype in ("spider", "spinner", "spinnerHalf"):
            if not has_solid_ground_below_range(ex, ey, patrol_tiles):
                print(f"Skipping {etype} at ({ex},{ey}) — insufficient ground below")
                etype = "bat"
                settings = type_settings["bat"]
                sprite_data = ENEMY_SPRITES.get("bat", {})
                sprite_paths = sprite_data.get("fly", [])

        if etype == "bat" and above_tile == "X":
            sprite_paths = sprite_data.get("hang", sprite_data.get("fly", []))

        try:
            enemy = Enemy(
                ex * TILE_SIZE,
                ey * TILE_SIZE + settings["y_offset"],
                patrol_width=settings["patrol_width"],
                sprite_paths=sprite_paths,
            )
            group.add(enemy)
        except Exception as e:
            print(f"Enemy creation failed ({etype}):", e)

    return group


enemies = make_enemies_from_tilemap(tilemap)
score = 0
lives = 3
coins_collected = 0
await_continue = False

class Camera:
    def __init__(self): self.x = 0; self.y = 0
cam = Camera()

def center_camera_on(px, py):
    cam.x = max(0, px - WIDTH // 2)
    cam.y = max(0, py - HEIGHT // 2)

def world_rect_from_tile(tx, ty):
    return pygame.Rect(tx * TILE_SIZE, ty * TILE_SIZE, TILE_SIZE, TILE_SIZE)

checkpoint_pos = RESPAWN_POS
checkpoint_active = False
checkpoint_tile = None
dead = False
game_over = False
death_time = 0
victory = False

def respawn_player(at_checkpoint=True):
    """
    Place player at checkpoint (if active and requested) or level start spawn.
    Ensures player is within level bounds and resets movement safely.
    """
    global player, checkpoint_pos, RESPAWN_POS, FIXED_SPAWN_POS

    try:
        if at_checkpoint and checkpoint_active and checkpoint_pos:
            spawn_x, spawn_y = checkpoint_pos
        else:
            spawn_x, spawn_y = FIXED_SPAWN_POS
    except Exception:
        spawn_x, spawn_y = 64, 64

    player.rect.topleft = (int(spawn_x), int(spawn_y))
    player.vx = 0
    player.vy = 0
    player.invulnerable = 120  
    player.on_ground = False
    player.can_double_jump = True
    player.facing_right = True
    try:
        player.collidable = True
    except Exception:
        pass

    try:
        center_camera_on(player.rect.centerx, player.rect.centery)
    except Exception:
        pass

    try:
        play_music("game")
    except Exception:
        pass

    global dead, await_continue, game_over
    dead = False
    await_continue = False
    game_over = False if lives > 0 else game_over

    print(f"[respawn] Player respawned at ({spawn_x}, {spawn_y})")


def full_restart(start_level_idx=0, keep_lives=False, keep_score=False):
    """
    start_level_idx: index of level to load
    keep_lives: if True, don't reset lives/counts 
    """
    global score, lives, tilemap, enemies, coins_collected
    global checkpoint_pos, checkpoint_active, current_level
    global victory, level_path, dead, await_continue, game_over

    current_level = start_level_idx

    if not keep_score:
        score = 0
    coins_collected = 0
    if not keep_lives:
        lives = 3
    victory = False
    level_path = level_path_for(current_level)
    tilemap = TileMap(str(level_path))
    enemies = make_enemies_from_tilemap(tilemap)

    global FIXED_SPAWN_POS
    FIXED_SPAWN_POS = find_safe_spawn(tilemap, fallback=(100, 100))
    checkpoint_pos = FIXED_SPAWN_POS
    checkpoint_active = False
    checkpoint_pos = None
    checkpoint_tile = None
    checkpoint_effects = []
    hud.checkpoint_timer = 0



    dead = False
    await_continue = False
    game_over = False

    respawn_player(at_checkpoint=False)
    try:
        play_music("game")
    except Exception:
        pass
    return tilemap, enemies


def start_specific_level(filename):
    global current_level, LEVEL_FILES, tilemap, enemies
    global checkpoint_pos, checkpoint_active, checkpoint_tile, level_path
    global dead, await_continue, game_over, victory
    global checkpoint_effects, hud

    checkpoint_active = False
    checkpoint_pos = None
    checkpoint_tile = None
    checkpoint_effects = []
    hud.checkpoint_timer = 0
    global score
    score = 0 
    dead = False
    await_continue = False
    game_over = False
    victory = False

    try:
        LEVEL_FILES[:] = discover_levels()
    except Exception as e:
        print("discover_levels error:", e)
        LEVEL_FILES[:] = ["level1.txt", "level2.txt", "level3.txt"]

    fname = os.path.basename(filename)
    if fname in LEVEL_FILES:
        current_level = LEVEL_FILES.index(fname)
    else:
        print(f"[start_specific_level] requested level '{filename}' not in LEVEL_FILES -> falling back to 0")
        current_level = 0

    level_path = level_path_for(current_level)
    if not level_path.exists():
        print(f"[start_specific_level] level file missing: {level_path}; falling back to level 0")
        current_level = 0
        level_path = level_path_for(0)

    try:
        tilemap = TileMap(str(level_path))
        enemies = make_enemies_from_tilemap(tilemap)
        checkpoint_effects = [CheckpointEffect(tx, ty) for tx, ty in tilemap.checkpoints()]
        FIXED_SPAWN_POS = find_safe_spawn(tilemap, fallback=(100, 100))
        checkpoint_pos = FIXED_SPAWN_POS
        checkpoint_active = False
        checkpoint_tile = None
        respawn_player(at_checkpoint=False)
        try:
            play_music("game")
        except Exception:
            pass
    except Exception as e:
        print("Error loading level:", level_path, e)
        current_level = 0
        level_path = level_path_for(0)
        tilemap = TileMap(str(level_path))
        enemies = make_enemies_from_tilemap(tilemap)
        checkpoint_effects = [CheckpointEffect(tx, ty) for tx, ty in tilemap.checkpoints()]
        respawn_player(at_checkpoint=False)

def menu_start_cb():
    global dead, await_continue, game_over, victory
    dead = False
    await_continue = False
    game_over = False
    victory = False
    score = 0
    full_restart(0)


def menu_levels_cb(filename=None):
    global score
    if filename:
        try:
            score = 0
            start_specific_level(filename)
            return "start"
        except Exception as e:
            print("menu_levels_cb (start) error:", e)
            return "back"
    res = show_levels_menu(screen, clock, font, start_cb=start_specific_level)
    return res

def menu_settings_cb():
    return show_settings_menu(screen, clock, font)

ret = show_main_menu(screen, clock, font, start_cb=menu_start_cb, levels_cb=menu_levels_cb, settings_cb=menu_settings_cb)
if ret == "quit":
    stop_music(); pygame.quit(); sys.exit()

try:
    play_music("game")
except Exception:
    pass

PAUSE_BTN = pygame.Rect(WIDTH - 92, 12, 80, 32)
DASH_KEYS = (pygame.K_LSHIFT, pygame.K_RSHIFT, pygame.K_e)

import speech_recognition as sr
import random

SPEECH_WORDS = ["jump", "banana", "restart", "gravity", "checkpoint", "speed", "coin", "level", "enemy", "dash", "run", "jump", "tres"]

current_speech_word = None
speech_prompt_time = 0

def listen_for_word(target, timeout=5):
    recognizer = sr.Recognizer()
    spoken_text = None
    try:
        with sr.Microphone() as source:
            print(f"🎤 Say the word: '{target}'")
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source, timeout=timeout)
        spoken_text = recognizer.recognize_google(audio).lower().strip()
        print("You said:", spoken_text)
        return spoken_text == target.lower(), spoken_text
    except sr.WaitTimeoutError:
        print("⏱ No speech detected.")
    except sr.UnknownValueError:
        print("🤔 Could not understand speech.")
    except sr.RequestError:
        print("⚠️ Speech recognition service error.")
    except Exception as e:
        print("Microphone or speech error:", e)
    return False, spoken_text


username = menu.current_user or "Guest"
save_score(username, score)
score = 0
hud = HUD(font, username=username)

running = True
while running:
    try:
        dt = clock.tick(60) / 1000.0
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False
                break
                    
            if ev.type == pygame.KEYDOWN:
                print("KEYDOWN:", ev.key, pygame.key.name(ev.key),
                      "game_over:", game_over, "dead:", dead,
                      "await_continue:", await_continue, "lives:", lives)
                
                if dead and await_continue:
                    if ev.key == pygame.K_c:
                        if current_speech_word:
                            print(f"[speech] Recording for word: {current_speech_word}")
                            correct, spoken_text = listen_for_word(current_speech_word)

                            if correct:
                                lives -= 0  
                                print("[speech] ✅ Correct! You said '{spoken_text}'. Reviving... lives left:", lives)

                                success_txt = font.render(f"Correct! You said '{spoken_text}'", True, (80, 255, 100))
                                screen.blit(success_txt, success_txt.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
                                pygame.display.flip()
                                pygame.time.delay(1000)

                                dead = False
                                await_continue = False
                                respawn_player(at_checkpoint=True)
                                try:
                                    play_music("game")
                                except:
                                    pass

                            else:
                                if spoken_text:
                                    print(f"[speech] Wrong! You said '{spoken_text}'. lives left:", lives)
                                    fail_txt = font.render(f"Wrong! You said '{spoken_text}'", True, (255, 80, 80))
                                else:
                                    print("[speech] No speech or not understood. lives left:", lives)
                                    fail_txt = font.render("No speech detected!", True, (255, 80, 80))
                                screen.blit(fail_txt, fail_txt.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
                                pygame.display.flip()
                                pygame.time.delay(1000)

                                if lives <= 0:
                                    game_over = True
                                    autosave_score(score)
                                    await_continue = False
                                    print("[speech] No lives left -> game over")

                            current_speech_word = None


                if game_over:
                    if ev.key == pygame.K_c:
                        print("[action] C pressed on Game Over")
                        if lives > 0:
                            lives -= 1
                            autosave_score(score)
                            print("[lives change] consumed on C (gameover) ->", lives)
                            game_over = False
                            dead = False
                            await_continue = False
                            respawn_player(at_checkpoint=True)
                            try: play_music("game")
                            except: pass
                        else:
                            print("[action] no lives left — cannot continue")
                        continue

                    if ev.key == pygame.K_r:
                        print("[action] R pressed on Game Over -> restart level")
                        autosave_score(score)
                        tilemap, enemies = full_restart(current_level, keep_score=False)
                        game_over = False
                        dead = False
                        await_continue = False
                        continue

                if ev.key == pygame.K_ESCAPE:
                    choice = show_pause_menu(screen, clock, font)
                    if choice == "quit":
                        autosave_score(score)
                        score = 0
                        running = False
                        break
                    if choice == "menu":
                        autosave_score(score)
                        score = 0
                        try: play_music("menu")
                        except: pass

                        checkpoint_active = False
                        checkpoint_pos = None
                        checkpoint_tile = None
                        checkpoint_effects = []
                        hud.checkpoint_timer = 0

                        ret = show_main_menu(screen, clock, font, 
                                             start_cb=menu_start_cb, 
                                             levels_cb=menu_levels_cb, 
                                             settings_cb=menu_settings_cb)
                        if ret == "quit":
                            running = False
                            break
                        continue

                        #tilemap, enemies = full_restart(0)
                    if choice == "restart":
                        autosave_score(score)
                        score = 0
                        tilemap, enemies = full_restart(current_level, keep_score=False)

                        continue
                    if choice == "settings":
                        sret = show_settings_menu(screen, clock, font)
                        try:
                            if _audio:
                                save_audio_settings(_audio.music_vol, _audio.sfx_vol)
                                set_volumes(music=_audio.music_vol, sfx=_audio.sfx_vol)
                        except: pass
                        continue

                if ev.key in DASH_KEYS:
                    keys = pygame.key.get_pressed()
                    dir_x = 0
                    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                        dir_x = -1
                    elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                        dir_x = 1
                    else:
                        dir_x = 1 if player.facing_right else -1
                    try:
                        if _audio: _audio.play_jump()
                    except: pass
                    player.try_dash(dir_x)
                    continue

                if ev.key == pygame.K_r and not game_over and not victory:
                    respawn_player()
                    continue

            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                if PAUSE_BTN.collidepoint(ev.pos):
                    choice = show_pause_menu(screen, clock, font)
                    if choice == "quit":
                        autosave_score(score)
                        score = 0
                        running = False
                        break
                    if choice == "menu":
                        autosave_score(score)
                        score = 0

                        try: play_music("menu")
                        except: pass

                        checkpoint_active = False
                        checkpoint_pos = None
                        checkpoint_tile = None
                        checkpoint_effects = []
                        hud.checkpoint_timer = 0

                        ret = show_main_menu(screen, clock, font,
                                            start_cb=menu_start_cb,
                                            levels_cb=menu_levels_cb,
                                            settings_cb=menu_settings_cb)
                        if ret == "quit":
                            running = False
                            break
                        continue
                    if choice == "restart":
                        autosave_score(score)
                        score = 0
                        tilemap, enemies = full_restart(current_level, keep_score=False)
                        continue
                    if choice == "settings":
                        show_settings_menu(screen, clock, font)
                        try:
                            if _audio:
                                save_audio_settings(_audio.music_vol, _audio.sfx_vol)
                                set_volumes(music=_audio.music_vol, sfx=_audio.sfx_vol)
                        except: pass
                        continue
                        
        if not game_over and not victory and not (dead and await_continue):
            keys = pygame.key.get_pressed()
            player.handle_input(keys)
            player.apply_physics()

            colliders = tilemap.coll_tiles() or []
            player.update(colliders, dt)

            for e in list(enemies):
                try:
                    e.update(colliders, dt)
                except Exception:
                    try: enemies.remove(e)
                    except: pass

            center_camera_on(player.rect.centerx, player.rect.centery)

            for cx, cy in list(tilemap.coins()):
                crect = world_rect_from_tile(cx, cy)
                if player.rect.colliderect(crect):
                    score += 10
                    coins_collected += 1
                    tilemap.remove_tile(cx, cy, 'C')
                    try: play_sfx("coin")
                    except: pass
                    if coins_collected % 3 == 0:
                        player.pickup_dash_refill()

            for px, py in tilemap.checkpoints():
                prect = world_rect_from_tile(px, py)
                if player.rect.colliderect(prect):
                    checkpoint_pos = (px * TILE_SIZE,
                                    py * TILE_SIZE - (TILE_SIZE//2))
                    checkpoint_active = True
                    checkpoint_tile = (px, py)
                    hud.trigger_checkpoint()
                    player.pickup_dash_refill()
                    player.can_double_jump = True

            reached_goal = False
            for gx, gy in tilemap.exits():
                grect = world_rect_from_tile(gx, gy)
                if player.rect.colliderect(grect):
                    reached_goal = True
                    break

            if reached_goal:
                current_level += 1
                if current_level >= len(LEVEL_FILES):
                    victory = True
                    game_over = False
                    dead = False
                    autosave_score(score)
                    score = 0
                    try: play_sfx("win")
                    except: pass
                    try: play_music("win")
                    except: pass
                else:
                    level_path = level_path_for(current_level)
                    tilemap = TileMap(str(level_path))
                    enemies = make_enemies_from_tilemap(tilemap)
                    checkpoint_pos = find_safe_spawn(tilemap,
                                                                  fallback=RESPAWN_POS)
                    checkpoint_active = False
                    hud.checkpoint_timer = 0
                    respawn_player(at_checkpoint=checkpoint_active)
                    pygame.time.delay(180)
                    continue

            died = False
            death_reason = None

            for sx, sy in list(tilemap.spikes()):
                srect = world_rect_from_tile(sx, sy)
                if player.rect.colliderect(srect) and player.invulnerable == 0:
                    died = True
                    death_reason = "spike"
                    break

            if not died and player.rect.top > HEIGHT + 200:
                died = True
                death_reason = "fall"

            if not died:
                for e in list(enemies):
                    if not getattr(e, "alive", True):
                        try: enemies.remove(e)
                        except: pass
                        continue
                    if player.rect.colliderect(e.rect):
                        if player.vy > 0 and player.rect.bottom - e.rect.top < 18:
                            e.alive = False
                            score += 15
                            player.vy = JUMP_VELOCITY / 2
                        else:
                            if player.invulnerable == 0:
                                died = True
                                death_reason = "enemy"
                                break

           
            if died:
                print(f"[death] died=True reason={death_reason} lives={lives} time={pygame.time.get_ticks()}")
                if lives <= 0:
                    game_over = True
                    dead = True
                    await_continue = False
                    death_time = pygame.time.get_ticks()
                    autosave_score(score)
                    score = 0
                    try: play_sfx("gameover")
                    except: pass
                    print("[death] no lives -> game over")
                else:

                    dead = True
                    await_continue = True
                    death_time = pygame.time.get_ticks()
                    player.vx = player.vy = 0
                    player.invulnerable = 0
                    current_speech_word = random.choice(SPEECH_WORDS)
                    speech_prompt_time = pygame.time.get_ticks()
                    print(f"[death] awaiting player speech '{current_speech_word}' — lives left: {lives}")


        else:
            pass

        if dead and not game_over and not victory and not await_continue:
            if pygame.time.get_ticks() - death_time > 200:
                respawn_player(at_checkpoint=checkpoint_active)

        if game_over or (dead and await_continue):
            keys = pygame.key.get_pressed()
            if keys[pygame.K_c]:
                pygame.time.delay(120)
                if lives > 0:
                    lives -= 1
                    print("[continue poll] consumed a life ->", lives)
                    game_over = False
                    dead = False
                    await_continue = False
                    respawn_player(at_checkpoint=True)
                    try: play_music("game")
                    except: pass
                else:
                    if dead and await_continue:
                        game_over = True
                        await_continue = False
                        print("[continue poll] no lives -> game over")
                    else:
                        print("[continue poll] no lives left")
            if keys[pygame.K_r]:
                pygame.time.delay(120)
                ttilemap, enemies = full_restart(current_level, keep_score=False)
                game_over = False
                dead = False
                await_continue = False
        hud.update(dt, score)
        background.draw(screen, cam)
        tileset = {'C': ICON_COIN} if ICON_COIN else None

        active = [checkpoint_tile] if checkpoint_active and checkpoint_tile is not None else []
        tilemap.draw(screen, cam, tileset_images=TILESET_IMAGES, active_checkpoints=active, dt=dt)

        for e in enemies:
            e.draw(screen, cam)
        player.draw(screen, cam)
        hud.draw(screen, score, lives, coins_collected, current_level + 1)


        pygame.draw.rect(screen, (28,28,36), PAUSE_BTN, border_radius=6)
        ptxt = font.render("Pause", True, (220,220,220))
        screen.blit(ptxt, (PAUSE_BTN.x + 12, PAUSE_BTN.y + 6))
        
        if dead and not game_over and not victory:
            if await_continue:
                if current_speech_word:
                    big_font = pygame.font.SysFont(None, 60)  # increase to 72 if you want it even bigger
                    main_txt = big_font.render(f"You died — say '{current_speech_word}' to continue!", True, (255, 220, 60))
                    screen.blit(main_txt, main_txt.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30)))

                    sub_font = pygame.font.SysFont(None, 32)
                    sub_txt = sub_font.render("Press C to start recording", True, (200, 200, 200))
                    screen.blit(sub_txt, sub_txt.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 30)))
                else:
                    listen_font = pygame.font.SysFont(None, 48)
                    listen_txt = listen_font.render("🎤 Listening...", True, (255, 220, 60))
                    screen.blit(listen_txt, listen_txt.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
            else:
                respawn_font = pygame.font.SysFont(None, 48)
                respawn_txt = respawn_font.render(f"Oof — respawning ({lives} lives left)", True, (255, 220, 60))
                screen.blit(respawn_txt, respawn_txt.get_rect(center=(WIDTH // 2, HEIGHT // 2)))


        if game_over and not victory:
            go_font = pygame.font.SysFont(None, 72)
            txt = go_font.render("GAME OVER", True, (255,30,30))
            screen.blit(txt, txt.get_rect(center=(WIDTH//2, HEIGHT//2 - 20)))
            small = font.render("Press R to restart (full reset)", True, (240,240,240))
            screen.blit(small, small.get_rect(center=(WIDTH//2, HEIGHT//2 + 36)))

        if victory:
            # autosave_score(score)
            # score = 0
            go_font = pygame.font.SysFont(None, 72)
            txt = go_font.render("YOU WIN!", True, (120,240,160))
            screen.blit(txt, txt.get_rect(center=(WIDTH//2, HEIGHT//2 - 20)))
            small = font.render("Press R to play again", True, (240,240,240))
            screen.blit(small, small.get_rect(center=(WIDTH//2, HEIGHT//2 + 36)))

        pygame.display.flip()

    except Exception:
        traceback.print_exc()
        running = False

stop_music()
pygame.quit()
sys.exit()
