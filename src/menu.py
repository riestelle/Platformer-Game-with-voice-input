# src/menu.py
import pygame, os, math, json
from settings import WIDTH, HEIGHT, BG_COLOR
import re
import random

import pygame, os, math, json, re, random
from settings import WIDTH, HEIGHT, BG_COLOR
from score_manager import save_score, get_score 

current_user = None
current_score = 0


ASSET_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "audio"))
CFG_PATH = os.path.join(os.path.dirname(__file__), "menu_config.json")

LAST_LEVEL_PATH = None

def load_sound(name):
    path = os.path.join(ASSET_DIR, name)
    try:
        return pygame.mixer.Sound(path)
    except Exception:
        return None

def load_music_path(name):
    path = os.path.join(ASSET_DIR, name)
    return path if os.path.exists(path) else None

class AudioManager:
    def __init__(self):
        try:
            pygame.mixer.init()
        except Exception:
            pass
        self.menu_music = load_music_path("music_menu.mp3")
        self.game_music = load_music_path("music_game.mp3")
        self.s_hover = load_sound("sfx_hover.mp3")
        self.s_select = load_sound("sfx_select.mp3")
        self.s_coin = load_sound("sfx_coin.mp3")
        self.s_jump = load_sound("sfx_jump.mp3")
        self.s_gameover = load_sound("sfx_gameover.mp3")
        self.s_win = load_sound("sfx_win.mp3")
        self.music_vol = 0.6
        self.sfx_vol = 0.9
        self.current = None
        self.apply_volumes()

    def apply_volumes(self):
        try:
            pygame.mixer.music.set_volume(self.music_vol)
            for s in (self.s_hover, self.s_select, self.s_coin, self.s_jump, self.s_gameover, self.s_win):
                if s:
                    s.set_volume(self.sfx_vol)
        except Exception:
            pass

    def play_music(self, which, fade_ms=200):
        path = self.menu_music if which == "menu" else (self.game_music if which == "game" else None)
        if not path: return
        try:
            if self.current != path:
                pygame.mixer.music.fadeout(fade_ms)
                pygame.mixer.music.load(path)
                pygame.mixer.music.set_volume(self.music_vol)
                pygame.mixer.music.play(-1)
                self.current = path
        except Exception:
            pass

    def stop_music(self, fade_ms=200):
        try:
            pygame.mixer.music.fadeout(fade_ms)
            self.current = None
        except Exception:
            pass

    def play_hover(self):
        if self.s_hover:
            try: self.s_hover.set_volume(self.sfx_vol); self.s_hover.play()
            except Exception: pass

    def play_select(self):
        if self.s_select:
            try: self.s_select.set_volume(self.sfx_vol); self.s_select.play()
            except Exception: pass

    def play_coin(self):
        if self.s_coin:
            try: self.s_coin.set_volume(self.sfx_vol); self.s_coin.play()
            except Exception: pass

    def play_jump(self):
        if self.s_jump:
            try: self.s_jump.set_volume(self.sfx_vol); self.s_jump.play()
            except Exception: pass

    def play_gameover(self):
        if self.s_gameover:
            try: self.s_gameover.set_volume(self.sfx_vol); self.s_gameover.play()
            except Exception: pass

    def play_win(self):
        if self.s_win:
            try: self.s_win.set_volume(self.sfx_vol); self.s_win.play()
            except Exception: pass

_audio = None
def ensure_audio():
    global _audio
    if _audio is None:
        _audio = AudioManager()
        try:
            if os.path.exists(CFG_PATH):
                with open(CFG_PATH, "r") as f:
                    cfg = json.load(f)
                _audio.music_vol = float(cfg.get("music_vol", _audio.music_vol))
                _audio.sfx_vol = float(cfg.get("sfx_vol", _audio.sfx_vol))
                _audio.apply_volumes()
        except Exception:
            pass
    return _audio

def save_audio_settings(music_vol, sfx_vol):
    try:
        cfg = {"music_vol": float(music_vol), "sfx_vol": float(sfx_vol)}
        with open(CFG_PATH, "w") as f:
            json.dump(cfg, f)
    except Exception:
        pass
def draw_button(surf, rect, text, hovered):
    base_color = (80, 90, 120)
    hover_color = (130, 160, 220)
    color = hover_color if hovered else base_color
    offset = -3 if hovered else 0

    pygame.draw.rect(surf, color, rect.move(0, offset), border_radius=10)
    if hovered:
        glow = pygame.Surface((rect.w+10, rect.h+10), pygame.SRCALPHA)
        pygame.draw.rect(glow, (150, 180, 255, 40), glow.get_rect(), border_radius=14)
        surf.blit(glow, (rect.x-5, rect.y-5))

def draw_text(surface, text, size, x, y, color=(240,240,240)):
    f = pygame.font.SysFont(None, size)
    r = f.render(text, True, color)
    surface.blit(r, r.get_rect(center=(x, y)))
    return r.get_rect(center=(x, y))

def fade(surface, alpha):
    s = pygame.Surface((WIDTH, HEIGHT))
    s.set_alpha(alpha)
    s.fill((0,0,0))
    surface.blit(s, (0,0))

class Button:
    def __init__(self, text, x, y, w=260, h=56):
        self.text = text
        self.rect = pygame.Rect(0,0,w,h)
        self.rect.center = (x,y)
        self.hovered = False
        self.hover_alpha = 0
        self.hover_offset = 0

    def draw(self, surf, selected=False):
        target_hover = selected or self.hovered
        if target_hover:
            self.hover_alpha = min(255, self.hover_alpha + 25)
            self.hover_offset = min(5, self.hover_offset + 1)
        else:
            self.hover_alpha = max(0, self.hover_alpha - 25)
            self.hover_offset = max(0, self.hover_offset - 1)

        base = (28,32,48)
        hover_col = (98,160,220)
        blend = self.hover_alpha / 255
        col = tuple(int(base[i] + (hover_col[i]-base[i]) * blend) for i in range(3))
        rect = self.rect.move(0, -self.hover_offset)

        pygame.draw.rect(surf, col, rect, border_radius=10)


        if self.hover_alpha > 0:
            glow = pygame.Surface((rect.w+14, rect.h+14), pygame.SRCALPHA)
            pygame.draw.rect(glow, (100,200,255,40), glow.get_rect(), border_radius=12)
            surf.blit(glow, (rect.x-7, rect.y-7))

        draw_text(surf, self.text, 28, rect.centerx, rect.centery, color=(245,245,245))

def draw_parallax(surf, t):
    band1 = (18,24,40)
    band2 = (26,34,60)
    surf.fill(BG_COLOR)
    for i in range(6):
        offset = math.sin((t*0.0006) + i) * 18
        pygame.draw.rect(surf, tuple(min(255,int(band1[j]+i*2)) for j in range(3)),
                         pygame.Rect(-200 + (i*260) + offset, HEIGHT//3 + i*8, 260, 120), border_radius=24)
    for i in range(5):
        offset = math.cos((t*0.0009) + i) * 28
        pygame.draw.rect(surf, tuple(min(255,int(band2[j]+i*1)) for j in range(3)),
                         pygame.Rect(-120 + (i*320) - offset, HEIGHT//1.9 + i*6, 320, 100), border_radius=20)

def show_main_menu(screen, clock, font, start_cb=None, levels_cb=None, settings_cb=None):
    pygame.event.clear()
    global LAST_LEVEL_PATH, current_user, score
    LAST_LEVEL_PATH = None
    audio = ensure_audio()
    if audio:
        audio.play_music("menu")

    #  Score setup 
    from score_manager import get_highest_score, get_score
    if not current_user:
        current_user = None

    # Initial score info
    user_score = get_score(current_user) if current_user else 0
    top_user, top_score = get_highest_score()

    t0 = pygame.time.get_ticks()
    login_rect = pygame.Rect(WIDTH - 160, 20, 140, 40)
    idx = 0
    particles = []

    # Buttons 
    buttons = [
        Button("Start Game", WIDTH // 2, HEIGHT // 2 - 10),
        Button("Levels", WIDTH // 2, HEIGHT // 2 + 68),
        Button("Settings", WIDTH // 2, HEIGHT // 2 + 146),
        Button("Quit", WIDTH // 2, HEIGHT // 2 + 224),
    ]

    #  Menu Loop 
    while True:
        dt = clock.tick(60)
        t = pygame.time.get_ticks()

        #  Events 
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                if audio: audio.stop_music()
                return "quit"

            if ev.type == pygame.KEYDOWN:
                if ev.key in (pygame.K_DOWN, pygame.K_s):
                    idx = (idx + 1) % len(buttons)
                    if audio: audio.play_hover()
                elif ev.key in (pygame.K_UP, pygame.K_w):
                    idx = (idx - 1) % len(buttons)
                    if audio: audio.play_hover()
                elif ev.key in (pygame.K_RETURN, pygame.K_z, pygame.K_SPACE):
                    if audio: audio.play_select()
                    txt = buttons[idx].text
                    if txt == "Start Game":
                        score = 0
                        if start_cb:
                            path = LAST_LEVEL_PATH if LAST_LEVEL_PATH and os.path.exists(LAST_LEVEL_PATH) else None
                            start_cb(path) if path else start_cb()
                        if audio: audio.play_music("game")
                        return "start"
                    elif txt == "Levels" and levels_cb:
                        score = 0
                        res = show_levels_menu(screen, clock, font, start_cb=levels_cb)
                        if res == "start": return "start"
                    elif txt == "Settings":
                        show_settings_menu(screen, clock, font)
                    elif txt == "Quit":
                        if audio: audio.stop_music()
                        return "quit"

            elif ev.type == pygame.MOUSEMOTION:
                for i, b in enumerate(buttons):
                    prev = b.hovered
                    b.hovered = b.rect.collidepoint(ev.pos)
                    if b.hovered and not prev and audio:
                        audio.play_hover()
                    if b.hovered:
                        idx = i

            elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                #  Login Button 
                if login_rect.collidepoint(ev.pos):
                    if audio: audio.play_select()
                    current_user = show_login_prompt(screen, clock, font)
                    user_score = get_score(current_user) if current_user else 0
                    top_user, top_score = get_highest_score()
                    continue

                #  Menu Buttons 
                for i, b in enumerate(buttons):
                    if b.rect.collidepoint(ev.pos):
                        if audio: audio.play_select()
                        txt = b.text
                        if txt == "Start Game":
                            score = 0
                            if start_cb:
                                path = LAST_LEVEL_PATH if LAST_LEVEL_PATH and os.path.exists(LAST_LEVEL_PATH) else None
                                start_cb(path) if path else start_cb()
                            if audio: audio.play_music("game")
                            return "start"
                        elif txt == "Levels" and levels_cb:
                            res = show_levels_menu(screen, clock, font, start_cb=levels_cb)
                            if res == "start": return "start"
                        elif txt == "Settings":
                            show_settings_menu(screen, clock, font)
                        elif txt == "Quit":
                            if audio: audio.stop_music()
                            return "quit"

        #  Background & Particles 
        draw_parallax(screen, t)
        for p in particles[:]:
            p[1] -= 0.3
            p[2] -= 1
            if p[2] <= 0:
                particles.remove(p)
            else:
                pygame.draw.circle(screen, (180, 200, 255, p[2]), (int(p[0]), int(p[1])), 2)
        if random.random() < 0.05:
            particles.append([random.randint(0, WIDTH), HEIGHT, random.randint(100, 200)])

        # Title & Subtitle 
        elapsed = t * 0.002
        title_y = HEIGHT // 4 + math.sin(elapsed) * 6
        title_scale = 1 + math.sin(elapsed * 0.5) * 0.03
        title_font = pygame.font.Font(None, int(64 * title_scale))
        title_text = title_font.render("Plataforma", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(WIDTH // 2, title_y))

        # Glow effect
        glow = pygame.Surface((title_rect.width + 40, title_rect.height + 40), pygame.SRCALPHA)
        glow_center = (glow.get_width() // 2, glow.get_height() // 2)
        for i in range(20):
            radius = (title_rect.height // 2) + i
            alpha = max(0, 40 - i * 2)
            pygame.draw.circle(glow, (120, 180, 255, alpha), glow_center, radius)
        screen.blit(glow, (title_rect.centerx - glow_center[0], title_rect.centery - glow_center[1]))
        screen.blit(title_text, title_rect)
        draw_text(screen, "a small experimental platformer", 20, WIDTH // 2, title_y + 42, color=(200, 200, 220))

        #  Buttons 
        for i, b in enumerate(buttons):
            b.draw(screen, selected=(i == idx))

        # Footer 
        footer = font.render("Use Arrows / WASD + Z/Enter or click", True, (200, 200, 220))
        screen.blit(footer, (WIDTH // 2 - footer.get_width() // 2, HEIGHT - 44))

        # Fade-in
        alpha = max(0, 255 - int((t - t0) * 0.6))
        if alpha > 0:
            fade(screen, alpha)

        # Login Button 
        pygame.draw.rect(screen, (50, 60, 90), login_rect, border_radius=10)
        draw_text(screen, "Logout" if current_user else "Login", 22, login_rect.centerx, login_rect.centery)

        #  Score Info
        if current_user:
            info_x, info_y = 20, 20
            pygame.draw.rect(screen, (40, 50, 80), (info_x - 10, info_y - 6, 250, 80), border_radius=10)
            draw_text(screen, f"User: {current_user}", 20, info_x + 110, info_y + 12, color=(220, 240, 255))
            draw_text(screen, f"Your Best: {user_score}", 20, info_x + 110, info_y + 36, color=(240, 220, 160))
            draw_text(screen, f"Top: {top_user or 'N/A'} - {top_score}", 18, info_x + 110, info_y + 60, color=(190, 210, 240))
        else:
            draw_text(screen, "Login to save your score", 18, 180, 40, color=(180, 190, 210))
            draw_text(screen, f"Top Player: {top_user or 'N/A'} ({top_score})", 18, 180, 62, color=(200, 210, 230))

        pygame.display.flip()

def show_login_prompt(screen, clock, font):
    """Shows a popup text input for username login."""
    username = ""
    active = True

    while active:
        clock.tick(60)
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return None
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_RETURN:
                    return username.strip() or None
                elif ev.key == pygame.K_ESCAPE:
                    return None
                elif ev.key == pygame.K_BACKSPACE:
                    username = username[:-1]
                else:
                    if len(username) < 15 and ev.unicode.isprintable():
                        username += ev.unicode

        #  Draw popup background 
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        #  Draw input box 
        draw_text(screen, "Enter Username", 36, WIDTH // 2, HEIGHT // 2 - 80)
        pygame.draw.rect(screen, (80, 90, 120),
                         (WIDTH // 2 - 150, HEIGHT // 2 - 20, 300, 40),
                         border_radius=8)
        draw_text(screen, username or "Type here...", 28,
                  WIDTH // 2, HEIGHT // 2, color=(240, 240, 240))

        pygame.display.flip()

def show_levels_menu(screen, clock, font, start_cb=None):
    global LAST_LEVEL_PATH  
    pygame.event.clear()
    audio = ensure_audio()
    levels_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "levels"))
    try:
        names = sorted([f for f in os.listdir(levels_dir) if f.lower().endswith(".txt")])
    except Exception as e:
        print("show_levels_menu: cannot list levels:", e)
        names = []

    spacing = 54
    top = HEIGHT // 4
    button_w = 520
    visible_rows = max(4, (HEIGHT - top - 160) // spacing)
    scroll_offset = 0
    idx = 0  

    back_button = Button("Back", WIDTH // 2, HEIGHT - 80, w=300)

    def clamp_selection():
        nonlocal idx, scroll_offset
        n = len(names)
        if n == 0:
            idx = 0
            scroll_offset = 0
            return
        idx = max(0, min(idx, n - 1))
        if idx < scroll_offset:
            scroll_offset = idx
        elif idx >= scroll_offset + visible_rows:
            scroll_offset = idx - visible_rows + 1

    clamp_selection()

    while True:
        dt = clock.tick(60)
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return "back"

            if ev.type == pygame.KEYDOWN:
                if ev.key in (pygame.K_DOWN, pygame.K_s):
                    if len(names) > 0:
                        idx = (idx + 1) % len(names)
                        clamp_selection()
                        if audio: audio.play_hover()
                elif ev.key in (pygame.K_UP, pygame.K_w):
                    if len(names) > 0:
                        idx = (idx - 1) % len(names)
                        clamp_selection()
                        if audio: audio.play_hover()
                elif ev.key in (pygame.K_RETURN, pygame.K_z, pygame.K_SPACE):
                    if len(names) == 0:
                        if audio: audio.play_select()
                        return "back"
                    chosen_name = names[idx]
                    chosen_path = os.path.join(levels_dir, chosen_name)
                    print("[menu] starting level:", chosen_path)
                    LAST_LEVEL_PATH = chosen_path
                    start_cb(chosen_path)

                    if start_cb:
                        try:
                            start_cb(chosen)
                        except Exception as e:
                            print("start_cb error:", e)
                            return "back"
                    if audio: audio.play_music("game")
                    return "start"

            if ev.type == pygame.MOUSEMOTION:
                mx, my = ev.pos
                start_i = scroll_offset
                end_i = min(scroll_offset + visible_rows, len(names))
                hovered_any = False
                for v, global_i in enumerate(range(start_i, end_i)):
                    y = top + v * spacing
                    b_rect = pygame.Rect(WIDTH//2 - (button_w//2), y - 22, button_w, 44)
                    if b_rect.collidepoint(ev.pos):
                        if audio and global_i != idx:
                            audio.play_hover()
                        idx = global_i
                        hovered_any = True
                        break
                back_button.hovered = back_button.rect.collidepoint(ev.pos) and not hovered_any

            if ev.type == pygame.MOUSEBUTTONDOWN:
                if ev.button == 1:
                    start_i = scroll_offset
                    end_i = min(scroll_offset + visible_rows, len(names))
                    clicked_any = False
                    for v, global_i in enumerate(range(start_i, end_i)):
                        y = top + v * spacing
                        b_rect = pygame.Rect(WIDTH//2 - (button_w//2), y - 22, button_w, 44)
                        if b_rect.collidepoint(ev.pos):
                            idx = global_i
                            chosen_name = names[idx]
                            chosen_path = os.path.join(levels_dir, chosen_name)  
                            if audio: audio.play_select()
                            print("[menu] starting level (click):", chosen_name)
                            LAST_LEVEL_PATH = chosen_path 
                            if start_cb:
                                try:
                                    start_cb(chosen_path)
                                except Exception as e:
                                    print("start_cb error:", e)
                                    return "back"
                            if audio: audio.play_music("game")
                            return "start"
                    if back_button.rect.collidepoint(ev.pos):
                        if audio: audio.play_select()
                        return "back"

                elif ev.button == 4:
                    if len(names) > 0:
                        idx = max(0, idx - 1)
                        clamp_selection()
                        if audio: audio.play_hover()
                elif ev.button == 5:
                    if len(names) > 0:
                        idx = min(len(names) - 1, idx + 1)
                        clamp_selection()
                        if audio: audio.play_hover()

            if ev.type == pygame.MOUSEWHEEL:
                if len(names) > 0:
                    idx = max(0, min(len(names) - 1, idx - ev.y))
                    clamp_selection()
                    if audio: audio.play_hover()

        draw_parallax(screen, pygame.time.get_ticks())
        draw_text(screen, "Choose Level", 44, WIDTH//2, HEIGHT//6, color=(230,230,250))

        if len(names) == 0:
            draw_text(screen, "No levels found in levels/ (put .txt files there)", 20, WIDTH//2, top + 20, color=(220,180,180))
        else:
            start_i = scroll_offset
            end_i = min(scroll_offset + visible_rows, len(names))
            for v, global_i in enumerate(range(start_i, end_i)):
                y = top + v * spacing
                fname = os.path.splitext(names[global_i])[0]
                text = re.sub(r"(\D)(\d)", r"\1 \2", fname.replace("_", " ").capitalize())

                selected = (global_i == idx)
                btn = Button(text, WIDTH//2, y, w=button_w)
                btn.hovered = selected
                btn.draw(screen, selected=selected)

            if len(names) > visible_rows:
                bar_h = int((visible_rows / len(names)) * (visible_rows * spacing))
                bar_h = max(bar_h, 24)
                scrollbar_x = WIDTH//2 + (button_w//2) + 16
                track_y = top
                track_h = visible_rows * spacing
                thumb_y = int(track_y + (scroll_offset / max(1, len(names) - visible_rows)) * (track_h - bar_h))
                pygame.draw.rect(screen, (50,50,60), (scrollbar_x, track_y, 8, track_h), border_radius=4)
                pygame.draw.rect(screen, (200,200,220), (scrollbar_x, thumb_y, 8, bar_h), border_radius=4)

        back_button.draw(screen, selected=False)
        pygame.display.flip()

def show_settings_menu(screen, clock, font):
    pygame.event.clear()
    audio = ensure_audio()
    music = audio.music_vol if audio else 0.6
    sfx = audio.sfx_vol if audio else 0.9
    back_btn = Button("Back", WIDTH//2, HEIGHT - 70, w=180)
    idx = 0
    while True:
        dt = clock.tick(60)
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return "back"
            if ev.type == pygame.KEYDOWN:
                if ev.key in (pygame.K_ESCAPE, pygame.K_z):
                    if audio:
                        audio.music_vol = music; audio.sfx_vol = sfx; audio.apply_volumes()
                        save_audio_settings(music, sfx)
                    return "back"
                if ev.key in (pygame.K_TAB, pygame.K_DOWN, pygame.K_UP):
                    idx = (idx + 1) % 2
                if ev.key in (pygame.K_LEFT, pygame.K_a):
                    if idx == 0: music = max(0.0, music - 0.05)
                    if idx == 1: sfx = max(0.0, sfx - 0.05)
                    if audio: audio.music_vol = music; audio.sfx_vol = sfx; audio.apply_volumes(); audio.play_hover()
                if ev.key in (pygame.K_RIGHT, pygame.K_d):
                    if idx == 0: music = min(1.0, music + 0.05)
                    if idx == 1: sfx = min(1.0, sfx + 0.05)
                    if audio: audio.music_vol = music; audio.sfx_vol = sfx; audio.apply_volumes(); audio.play_hover()
                if ev.key in (pygame.K_RETURN, pygame.K_SPACE):
                    if audio: audio.play_select()
                    audio.music_vol = music; audio.sfx_vol = sfx; audio.apply_volumes()
                    save_audio_settings(music, sfx)
                    return "back"
            if ev.type == pygame.MOUSEMOTION:
                back_btn.hovered = back_btn.rect.collidepoint(ev.pos)
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                if back_btn.rect.collidepoint(ev.pos):
                    if audio: audio.play_select()
                    audio.music_vol = music; audio.sfx_vol = sfx; audio.apply_volumes()
                    save_audio_settings(music, sfx)
                    return "back"
                mx,my = ev.pos
                music_rect = pygame.Rect(WIDTH//2-160, HEIGHT//2-20, 320, 20)
                sfx_rect = pygame.Rect(WIDTH//2-160, HEIGHT//2+40, 320, 20)
                if music_rect.collidepoint(ev.pos):
                    rel = (mx - music_rect.x) / music_rect.w
                    music = max(0.0, min(1.0, rel))
                    if audio: audio.music_vol = music; audio.apply_volumes(); audio.play_hover()
                if sfx_rect.collidepoint(ev.pos):
                    rel = (mx - sfx_rect.x) / sfx_rect.w
                    sfx = max(0.0, min(1.0, rel))
                    if audio: audio.sfx_vol = sfx; audio.apply_volumes(); audio.play_hover()

        screen.fill(BG_COLOR)
        draw_text(screen, "Settings", 44, WIDTH//2, 80, color=(230,230,250))
        draw_text(screen, "Music Volume", 22, WIDTH//2, HEIGHT//2-40)
        music_rect = pygame.Rect(WIDTH//2-160, HEIGHT//2-20, 320, 20)
        pygame.draw.rect(screen, (80,80,90), music_rect, border_radius=8)
        pygame.draw.rect(screen, (120,190,240), (music_rect.x, music_rect.y, int(music_rect.w * music), music_rect.h), border_radius=8)
        draw_text(screen, "SFX Volume", 22, WIDTH//2, HEIGHT//2+20)
        sfx_rect = pygame.Rect(WIDTH//2-160, HEIGHT//2+40, 320, 20)
        pygame.draw.rect(screen, (80,80,90), sfx_rect, border_radius=8)
        pygame.draw.rect(screen, (140,220,140), (sfx_rect.x, sfx_rect.y, int(sfx_rect.w * sfx), sfx_rect.h), border_radius=8)
        back_btn.draw(screen, selected=False)
        draw_text(screen, f"{int(music*100)}%", 18, WIDTH//2 + 200, HEIGHT//2-20)
        draw_text(screen, f"{int(sfx*100)}%", 18, WIDTH//2 + 200, HEIGHT//2+40)
        pygame.display.flip()

def show_pause_menu(screen, clock, font):
    pygame.event.clear()
    audio = ensure_audio()
    buttons = [
        Button("Resume", WIDTH//2, HEIGHT//2 - 30, w=260),
        Button("Restart Level", WIDTH//2, HEIGHT//2 + 30, w=260),
        Button("Settings", WIDTH//2, HEIGHT//2 + 90, w=260),
        Button("Exit to Menu", WIDTH//2, HEIGHT//2 + 150, w=260),
        Button("Exit Game", WIDTH//2, HEIGHT//2 + 210, w=260),
    ]
    idx = 0
    while True:
        dt = clock.tick(60)
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return "quit"
            if ev.type == pygame.KEYDOWN:
                if ev.key in (pygame.K_ESCAPE, pygame.K_z):
                    if audio: audio.play_select()
                    return "resume"
                if ev.key in (pygame.K_DOWN, pygame.K_s):
                    idx = (idx + 1) % len(buttons); audio.play_hover() if audio else None
                if ev.key in (pygame.K_UP, pygame.K_w):
                    idx = (idx - 1) % len(buttons); audio.play_hover() if audio else None
                if ev.key in (pygame.K_RETURN, pygame.K_z, pygame.K_SPACE):
                    if audio: audio.play_select()
                    txt = buttons[idx].text
                    if txt == "Resume":
                        return "resume"
                    if txt == "Restart Level":
                        return "restart"
                    if txt == "Settings":
                        return "settings"
                    if txt == "Exit to Menu":
                        return "menu"
                    if txt == "Exit Game":
                        return "quit"
            if ev.type == pygame.MOUSEMOTION:
                for i,b in enumerate(buttons):
                    prev = b.hovered
                    b.hovered = b.rect.collidepoint(ev.pos)
                    if b.hovered and not prev and audio: audio.play_hover()
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                for i,b in enumerate(buttons):
                    if b.rect.collidepoint(ev.pos):
                        if audio: audio.play_select()
                        txt = b.text
                        if txt == "Resume":
                            return "resume"
                        if txt == "Restart Level":
                            return "restart"
                        if txt == "Settings":
                            return "settings"
                        if txt == "Exit to Menu":
                            return "menu"
                        if txt == "Exit Game":
                            return "quit"

        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((10,10,12,200))
        screen.blit(overlay, (0,0))
        draw_text(screen, "PAUSED", 48, WIDTH//2, HEIGHT//3, color=(240,240,240))
        for i,b in enumerate(buttons):
            b.draw(screen, selected=(i==idx))
        pygame.display.flip()