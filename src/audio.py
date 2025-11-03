# src/audio.py
import os
import pygame

ASSET_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "audio"))

FILE_MAP = {
    "music_menu":  "music_menu.mp3",
    "music_game":  "music_game.mp3",
    "music_gameover": "music_gameover.mp3", 
    "music_win":   "music_win.mp3",         
    "sfx_hover":   "sfx_hover.mp3",
    "sfx_select":  "sfx_select.mp3",
    "sfx_coin":    "sfx_coin.mp3",
    "sfx_jump":    "sfx_jump.mp3",
    "sfx_gameover":"sfx_gameover.mp3",
    "sfx_win":     "sfx_win.mp3",
    "sfx_correct": "sfx_correct.mp3",
    "sfx_incorrect":"sfx_incorrect.mp3",
}

_initialized = False
_music_playing = None
_sounds = {}
_music_volume = 0.6
_sfx_volume = 0.9

def _path_for(key):
    name = FILE_MAP.get(key)
    if not name:
        return None
    p = os.path.join(ASSET_DIR, name)
    if os.path.exists(p):
        return p
    base, _ = os.path.splitext(p)
    for ext in (".mp3", ".ogg", ".wav"):
        alt = base + ext
        if os.path.exists(alt):
            return alt
    return None

def init_audio(music_vol=0.6, sfx_vol=0.9):
    """
    Initialize pygame mixer and preload SFX.
    Call once after pygame.init().
    """
    global _initialized, _sfx_volume, _music_volume, _sounds
    if _initialized:
        return
    try:
        pygame.mixer.init()
    except Exception:
        pass
    _music_volume = float(music_vol)
    _sfx_volume = float(sfx_vol)
    for k in ("sfx_hover", "sfx_select", "sfx_coin", "sfx_jump", "sfx_gameover", "sfx_win"):
        p = _path_for(k)
        if p:
            try:
                s = pygame.mixer.Sound(p)
                s.set_volume(_sfx_volume)
                _sounds[k] = s
            except Exception:
                _sounds[k] = None
        else:
            _sounds[k] = None
    _initialized = True

def play_music(which="menu", loop=-1, fade_ms=300):
    """which: 'menu', 'game', 'gameover', 'win'"""
    global _music_playing, _music_volume
    if not _initialized:
        init_audio()
    key = "music_menu" if which == "menu" else ("music_game" if which == "game" else ("music_gameover" if which == "gameover" else ("music_win" if which == "win" else None)))
    if key is None:
        return
    path = _path_for(key)
    if not path:
        return
    try:
        if _music_playing != path:
            pygame.mixer.music.fadeout(fade_ms)
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(_music_volume)
            pygame.mixer.music.play(loop)
            _music_playing = path
    except Exception:
        pass

def stop_music(fade_ms=200):
    try:
        pygame.mixer.music.fadeout(fade_ms)
    except Exception:
        pass

def play_sfx(name):
    """
    name: 'hover','select','coin','jump','gameover','win'
    """
    if not _initialized:
        init_audio()
    key = f"sfx_{name}"
    snd = _sounds.get(key)
    if snd:
        try:
            snd.set_volume(_sfx_volume)
            snd.play()
        except Exception:
            pass

def set_volumes(music=None, sfx=None):
    global _music_volume, _sfx_volume
    if music is not None:
        _music_volume = max(0.0, min(1.0, float(music)))
        try:
            pygame.mixer.music.set_volume(_music_volume)
        except Exception:
            pass
    if sfx is not None:
        _sfx_volume = max(0.0, min(1.0, float(sfx)))
        for snd in _sounds.values():
            try:
                if snd: snd.set_volume(_sfx_volume)
            except Exception:
                pass