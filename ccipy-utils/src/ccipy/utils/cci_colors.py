from math import sqrt

# ---------------------------------------------------------------------------
# Named colors
# ---------------------------------------------------------------------------


def rgb_color(r: int, g: int, b: int, a: int = 255) -> int:
    """
    Create an OMERO ARGB color integer from 0-255 RGBA components.

    OMERO stores colors as 32-bit ARGB ints: 0xAARRGGBB
    """
    if not all(0 <= v <= 255 for v in (r, g, b, a)):
        raise ValueError("RGBA components must be in 0..255")
    return (a << 24) | (r << 16) | (g << 8) | b


color_type = int


class Colors:
    """
    Common named colors as OMERO ARGB ints.

    Alpha is always 255 (fully opaque).
    """

    # Basic
    BLACK = rgb_color(0, 0, 0)
    WHITE = rgb_color(255, 255, 255)
    GRAY = rgb_color(128, 128, 128)
    LIGHT_GRAY = rgb_color(192, 192, 192)
    DARK_GRAY = rgb_color(64, 64, 64)

    RED = rgb_color(255, 0, 0)
    GREEN = rgb_color(0, 255, 0)
    BLUE = rgb_color(0, 0, 255)
    CYAN = rgb_color(0, 255, 255)
    MAGENTA = rgb_color(255, 0, 255)
    YELLOW = rgb_color(255, 255, 0)

    # Some extra useful tones for channels/overlays
    ORANGE = rgb_color(255, 165, 0)
    PURPLE = rgb_color(128, 0, 128)
    LIME = rgb_color(191, 255, 0)
    TEAL = rgb_color(0, 128, 128)
    PINK = rgb_color(255, 192, 203)
    BROWN = rgb_color(139, 69, 19)
    GOLD = rgb_color(255, 215, 0)
    NAVY = rgb_color(0, 0, 128)
    OLIVE = rgb_color(128, 128, 0)
    MAROON = rgb_color(128, 0, 0)

    # Classic “RGB for channels”
    CHANNEL_RED = RED
    CHANNEL_GREEN = GREEN
    CHANNEL_BLUE = BLUE
    CHANNEL_CYAN = CYAN
    CHANNEL_MAGENTA = MAGENTA
    CHANNEL_YELLOW = YELLOW


# A mapping from lower-case names to ARGB values.
NAMED_COLORS: dict[str, int] = {
    # basic
    "black": Colors.BLACK,
    "white": Colors.WHITE,
    "gray": Colors.GRAY,
    "grey": Colors.GRAY,  # alias
    "lightgray": Colors.LIGHT_GRAY,
    "lightgrey": Colors.LIGHT_GRAY,
    "darkgray": Colors.DARK_GRAY,
    "darkgrey": Colors.DARK_GRAY,
    "red": Colors.RED,
    "green": Colors.GREEN,
    "blue": Colors.BLUE,
    "cyan": Colors.CYAN,
    "magenta": Colors.MAGENTA,
    "yellow": Colors.YELLOW,
    # extras
    "orange": Colors.ORANGE,
    "purple": Colors.PURPLE,
    "lime": Colors.LIME,
    "teal": Colors.TEAL,
    "pink": Colors.PINK,
    "brown": Colors.BROWN,
    "gold": Colors.GOLD,
    "navy": Colors.NAVY,
    "olive": Colors.OLIVE,
    "maroon": Colors.MAROON,
}


def get_color(name: str, default: int | None = None) -> int | None:
    """
    Look up a named color (case-insensitive).

    Example:
        get_color("red") -> Colors.RED

    Returns `default` (or None) if the name is unknown.
    """
    return NAMED_COLORS.get(name.replace(" ", "").lower(), default)


def to_named_color_exact(r, g, b):
    """
    Return the name of the color in NAMED_COLORS that exactly matches (r,g,b).
    Returns None if no exact match exists.
    """
    for name, argb in NAMED_COLORS.items():
        nr, ng, nb = to_rgb(argb)
        if (r, g, b) == (nr, ng, nb):
            return name
    return None


def to_named_color_nearest(r, g, b):
    """
    Return the closest named color using Euclidean distance in RGB space.
    """
    best_name = None
    best_dist = float("inf")

    for name, argb in NAMED_COLORS.items():
        nr, ng, nb = to_rgb(argb)
        dist = sqrt((r - nr)**2 + (g - ng)**2 + (b - nb)**2)
        if dist < best_dist:
            best_dist = dist
            best_name = name

    return best_name


# ---------------------------------------------------------------------------
# Conversion helpers (optional but handy)
# ---------------------------------------------------------------------------


def to_rgba(argb: int) -> tuple[int, int, int, int]:
    """
    Convert ARGB int -> (r, g, b, a).
    """
    a = (argb >> 24) & 0xFF
    r = (argb >> 16) & 0xFF
    g = (argb >> 8) & 0xFF
    b = argb & 0xFF
    return r, g, b, a


def to_rgb(argb: int) -> tuple[int, int, int]:
    """
    Convert ARGB int -> (r, g, b) (ignores alpha).
    """
    r, g, b, _ = to_rgba(argb)
    return r, g, b


def to_hex(argb: int, include_hash: bool = True) -> str:
    """
    Convert ARGB int -> '#RRGGBB' string (ignores alpha).
    """
    r, g, b = to_rgb(argb)
    prefix = "#" if include_hash else ""
    return f"{prefix}{r:02X}{g:02X}{b:02X}"
