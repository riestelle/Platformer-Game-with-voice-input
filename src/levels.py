import os

def load_level_from_path(path):
    """
    Canonical loader: given an absolute path to a .txt level file,
    parse it and return a TileMap (or perform the in-place setup).
    Adapt this to your project's loader functions.
    """
    from tilemap import TileMap  
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Level file not found: {path}")
    tilemap = TileMap(path)
    from enemy import make_enemies_from_tilemap
    enemies = make_enemies_from_tilemap(tilemap)
    return {"tilemap": tilemap, "enemies": enemies}