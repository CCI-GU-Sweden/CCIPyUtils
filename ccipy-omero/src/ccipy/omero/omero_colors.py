"""
omero_colors.py

Helpers and named colors for OMERO (Python).

Usage
-----
from omero_colors import Colors, as_rint, omero_color, hex_to_omero

channel = pixels.getChannel(0)
channel.setColor(as_rint(Colors.RED))
"""

from __future__ import annotations
from ccipy.utils.cci_colors import rgb_color
from omero.rtypes import rint


# ---------------------------------------------------------------------------
# Core helpers
# ---------------------------------------------------------------------------


# def omero_color(r: int, g: int, b: int, a: int = 255) -> int:
#     """
#     Create an OMERO ARGB color integer from 0-255 RGBA components.

#     OMERO stores colors as 32-bit ARGB ints: 0xAARRGGBB
#     """
#     if not all(0 <= v <= 255 for v in (r, g, b, a)):
#         raise ValueError("RGBA components must be in 0..255")
#     return (a << 24) | (r << 16) | (g << 8) | b


def hex_to_omero(hex_color: str, alpha: int = 255) -> int:
    """
    Convert a #RRGGBB or RRGGBB hex string to an OMERO ARGB int.
    """
    s = hex_color.strip().lstrip("#")
    if len(s) != 6:
        raise ValueError(f"Expected hex color of form #RRGGBB, got: {hex_color!r}")
    r = int(s[0:2], 16)
    g = int(s[2:4], 16)
    b = int(s[4:6], 16)
    return rgb_color(r, g, b, a=alpha)


def cci_color_to_omero_rint_color(color: int) -> rint:
    return as_rint(color)


def as_rint(argb: int):
    """
    Wrap an OMERO ARGB int as omero.rtypes.rint, ready for setColor().
    """
    
    if argb >= 2**31:
        argb -= 2**32

    return rint(argb)


def omero_rint_to_rgba(color_rint):
    """
    Convert OMERO shape.color (rint) into (r, g, b, a) tuple.
    Accepts either an rint object or a plain int.
    """
    # If it's an OMERO rint, extract its value
    try:
        argb = color_rint.val
    except AttributeError:
        argb = color_rint

    r = (argb >> 24) & 0xFF
    g = (argb >> 16) & 0xFF
    b = (argb >> 8) & 0xFF
    a = argb & 0xFF
    return r, g, b, a


def omero_rgb_to_rint(r: int, g: int, b: int):
    """Convert RGB components to an OMERO rint color (with alpha=255)."""
    return omero_rgba_to_rint(r, g, b, 255)


def omero_rgba_to_rint(r: int, g: int, b: int, a: int = 255):
    """Convert RGBA components to an OMERO rint color."""
    argb = (r << 24) | (g << 16) | (b << 8) | a
    return as_rint(argb)


def omero_rint_to_rgb(color_rint):
    """Return only (R, G, B)."""
    r, g, b, _ = omero_rint_to_rgba(color_rint)
    return r, g, b
