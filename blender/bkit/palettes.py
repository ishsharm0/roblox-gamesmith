"""Curated colour palettes (sRGB hex). Use a palette per scene and stay inside it.

Rules that keep stylised work looking designed:
- One dominant colour (60%), one secondary (30%), one accent (10%) per asset.
- Base values stay between about 0.15 and 0.85: no pure white or black surfaces.
- Neutrals (cream, stone, ink) carry most of a scene; saturated colours are for the focal object.

Refer to a colour anywhere in bkit as 'palette.name', e.g. materials.toy_plastic('toybox.red').
"""

PALETTES = {
    # Primary toy colours, slightly warm. Toys, UI-like props, kids' games.
    "toybox": {"red": "D7463F", "orange": "F28E2B", "yellow": "F6C445", "green": "5BB04B",
               "blue": "3A7BD5", "purple": "7E57C2", "cream": "F2E8D5", "ink": "33363D"},
    # Nature: grass, leaves, bark, sand, stone.
    "meadow": {"grass": "7CB342", "leaf": "4E9A3C", "pine": "2E6B4A", "bark": "7A5233",
               "sand": "E2C58F", "stone": "A7A39B", "sky": "8EC9EE", "flower": "E86A92"},
    # Pastels for cute/candy themes. Pair with toy_bright lighting.
    "candy": {"pink": "F49AC1", "mint": "8FD9B6", "lemon": "F7E07B", "lilac": "B9A3E3",
              "peach": "F7B58A", "sky": "9AD0F5", "cream": "FFF4E6", "berry": "C2457A"},
    # Castles and medieval toys.
    "fortress": {"stone": "C9C1B3", "stone_dark": "8E877C", "roof": "C8553D", "roof_dark": "9C3B2A",
                 "wood": "A8703F", "banner": "3E6FB0", "gold": "E8B547", "moss": "6E9E4A"},
    # Warm dusk: coral, apricot, plum.
    "sunset": {"coral": "F07167", "apricot": "F9A55A", "gold": "F6CF6B", "plum": "6B4A7A",
               "dusk": "3E4A7A", "sand": "EED9B7", "teal": "3C9D9B", "ink": "2A2438"},
    # Cold: ice, snow, deep sea, with warm accents.
    "arctic": {"ice": "CFE8F2", "snow": "EEF3F6", "sea": "3F88C5", "deep": "1D4E89",
               "slate": "5B6C7D", "berry": "D9415E", "orange": "F39237", "pine": "2E5E4E"},
    # Roblox BrickColors (classic avatar: yellow skin, blue torso, green legs).
    "roblox": {"bright_red": "C4281C", "bright_blue": "0D69AC", "bright_yellow": "F5CD30",
               "dark_green": "287F47", "lime": "A4BD47", "stone_grey": "A3A2A5",
               "reddish_brown": "694027", "white": "F2F3F3", "black": "1B2A35", "nougat": "CC8E69"},
    # Neutral product shots: off-whites and greys plus two accents.
    "product": {"white": "EDEBE6", "light": "C9C6C0", "mid": "8D8A85", "graphite": "3F4045",
                "orange": "E8692A", "blue": "2F6FDE"},
}


def get(name):
    """Return the palette dict {colour_name: hex} called `name` (see PALETTES)."""
    try:
        return PALETTES[name]
    except KeyError:
        raise KeyError(f"no palette {name!r}; have {sorted(PALETTES)}") from None


def names():
    """Names of all palettes."""
    return sorted(PALETTES)


def colors(name):
    """['palette.colour', ...] specs for every colour in a palette, in order."""
    return [f"{name}.{c}" for c in get(name)]
