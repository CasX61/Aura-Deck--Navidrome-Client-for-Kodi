#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 CasX61
"""
Render every bitmap Aura-Deck ships with.

Kodi skins can only draw textures, so icons, masks, gradients and glows are
generated here once and committed. Icons come from Google's Material Icons
(Apache 2.0, see tools/fonts), everything else is drawn procedurally.

    python3 tools/make_media.py
"""

import math
import os
import random

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ADDON = os.path.join(ROOT, 'script.auradeck')
MEDIA = os.path.join(ADDON, 'resources', 'skins', 'Default', 'media')
FONT = os.path.join(ROOT, 'tools', 'fonts', 'MaterialIconsRound-Regular.otf')
CODEPOINTS = os.path.join(ROOT, 'tools', 'fonts', 'MaterialIconsRound-Regular.codepoints')

VIOLET = (139, 92, 246)
CYAN = (34, 211, 238)
PINK = (236, 72, 153)
BG = (11, 12, 20)

# file name -> material icon name
ICONS = {
    'home': 'home',
    'search': 'search',
    'artist': 'person',
    'album': 'album',
    'playlist': 'queue_music',
    'favourite': 'favorite',
    'favourite_outline': 'favorite_border',
    'genre': 'category',
    'radio': 'radio',
    'offline': 'offline_pin',
    'download': 'download',
    'downloaded': 'download_done',
    'settings': 'settings',
    'play': 'play_arrow',
    'pause': 'pause',
    'next': 'skip_next',
    'prev': 'skip_previous',
    'shuffle': 'shuffle',
    'repeat': 'repeat',
    'repeat_one': 'repeat_one',
    'more': 'more_horiz',
    'queue': 'format_list_bulleted',
    'lyrics': 'lyrics',
    'mix': 'auto_awesome',
    'star': 'star',
    'note': 'music_note',
    'arrow': 'arrow_forward',
    'history': 'history',
    'add': 'add',
    'edit': 'edit',
    'delete': 'delete',
    'cloud_off': 'cloud_off',
    'equalizer': 'graphic_eq',
    'sort': 'sort',
    'person_round': 'account_circle',
}


def out(name):
    return os.path.join(MEDIA, name)


def load_codepoints():
    table = {}
    with open(CODEPOINTS, encoding='utf-8') as handle:
        for line in handle:
            parts = line.split()
            if len(parts) == 2:
                table[parts[0]] = chr(int(parts[1], 16))
    return table


# Icons that look centred only when nudged: a play triangle's visual weight
# sits left of its bounding box. Offsets are fractions of the icon size.
OPTICAL_OFFSET = {'play': (0.03, 0.0)}


def render_icon(glyph, size=96, scale=4, name=''):
    """
    Draw a Material glyph and centre its visible ink in the square. Font
    metrics are not reliable for this (PIL places icon glyphs by ascender),
    so the glyph is drawn on a larger canvas, cropped to its ink and pasted.
    """
    big = size * scale
    font = ImageFont.truetype(FONT, int(big * 0.84))
    canvas = Image.new('L', (big * 2, big * 2), 0)
    ImageDraw.Draw(canvas).text((big // 2, big // 2), glyph, font=font, fill=255)
    ink = canvas.crop(canvas.getbbox())
    dx, dy = OPTICAL_OFFSET.get(name, (0, 0))
    img = Image.new('L', (big, big), 0)
    img.paste(ink, (int((big - ink.width) / 2 + dx * big), int((big - ink.height) / 2 + dy * big)))
    alpha = img.resize((size, size), Image.LANCZOS)
    icon = Image.new('RGBA', (size, size), (255, 255, 255, 0))
    icon.putalpha(alpha)
    return icon


def rounded_mask(size, radius, scale=4):
    w, h = size
    big = Image.new('L', (w * scale, h * scale), 0)
    ImageDraw.Draw(big).rounded_rectangle(
        (0, 0, w * scale - 1, h * scale - 1), radius=radius * scale, fill=255)
    return big.resize((w, h), Image.LANCZOS)


def white_with_alpha(alpha):
    img = Image.new('RGBA', alpha.size, (255, 255, 255, 0))
    img.putalpha(alpha)
    return img


def save_rounded(name, size, radius):
    white_with_alpha(rounded_mask(size, radius)).save(out(name))


def save_circle(name, size):
    white_with_alpha(rounded_mask((size, size), size // 2)).save(out(name))


def save_ring(name, size, stroke):
    outer = rounded_mask((size, size), size // 2)
    inner = Image.new('L', (size, size), 0)
    inner.paste(rounded_mask((size - 2 * stroke, size - 2 * stroke), (size - 2 * stroke) // 2),
                (stroke, stroke))
    white_with_alpha(ImageChops.subtract(outer, inner)).save(out(name))


def save_frame(name, size, radius, stroke):
    outer = rounded_mask((size, size), radius)
    inner = Image.new('L', (size, size), 0)
    inner.paste(rounded_mask((size - 2 * stroke, size - 2 * stroke), radius - stroke),
                (stroke, stroke))
    white_with_alpha(ImageChops.subtract(outer, inner)).save(out(name))


def save_gradients():
    # Vertical: transparent at the top, opaque at the bottom.
    vert = Image.new('L', (4, 256))
    for y in range(256):
        t = y / 255
        value = int(255 * (t * t * (3 - 2 * t)))
        for x in range(4):
            vert.putpixel((x, y), value)
    white_with_alpha(vert).save(out('grad_v.png'))
    # Horizontal: opaque at the left, transparent at the right.
    horiz = vert.rotate(-90, expand=True)
    white_with_alpha(horiz).save(out('grad_h.png'))


def save_glow(name, size=256):
    img = Image.new('L', (size, size), 0)
    ImageDraw.Draw(img).ellipse((size * 0.22, size * 0.22, size * 0.78, size * 0.78), fill=255)
    img = img.filter(ImageFilter.GaussianBlur(size * 0.12))
    white_with_alpha(img).save(out(name))


def save_shadow(name, size=128, radius=24, blur=14):
    pad = blur * 2
    img = Image.new('L', (size, size), 0)
    ImageDraw.Draw(img).rounded_rectangle((pad, pad, size - pad, size - pad), radius=radius, fill=200)
    img = img.filter(ImageFilter.GaussianBlur(blur))
    shadow = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    shadow.putalpha(img)
    shadow.save(out(name))


def save_spinner(name, size=128, stroke=12):
    scale = 4
    big = Image.new('L', (size * scale, size * scale), 0)
    draw = ImageDraw.Draw(big)
    box = (stroke * scale, stroke * scale, (size - stroke) * scale, (size - stroke) * scale)
    for step in range(270):
        alpha = int(255 * (step / 270) ** 1.4)
        draw.arc(box, start=step - 90, end=step - 88, fill=alpha, width=stroke * scale)
    white_with_alpha(big.resize((size, size), Image.LANCZOS)).save(out(name))


def gradient_image(size, colors, angle=135):
    """Linear multi-stop gradient across the image at the given angle."""
    w, h = size
    img = Image.new('RGB', size)
    px = img.load()
    rad = math.radians(angle)
    dx, dy = math.cos(rad), math.sin(rad)
    span = abs(w * dx) + abs(h * dy)
    stops = len(colors) - 1
    for y in range(h):
        for x in range(w):
            t = ((x - w / 2) * dx + (y - h / 2) * dy) / span + 0.5
            t = min(max(t, 0.0), 1.0) * stops
            i = min(int(t), stops - 1)
            f = t - i
            a, b = colors[i], colors[i + 1]
            px[x, y] = tuple(int(a[c] + (b[c] - a[c]) * f) for c in range(3))
    return img


def save_accent():
    """Violet→cyan fills: progress bar, primary pill buttons, round accent buttons."""
    gradient_image((256, 64), [VIOLET, CYAN], angle=0).save(out('accent_h.png'))

    pill = gradient_image((320, 76), [VIOLET, CYAN], angle=0).convert('RGBA')
    pill.putalpha(rounded_mask((320, 76), 38))
    pill.save(out('btn_primary.png'))

    disc = gradient_image((128, 128), [VIOLET, CYAN], angle=45).convert('RGBA')
    disc.putalpha(rounded_mask((128, 128), 64))
    disc.save(out('btn_accent.png'))


def save_bars():
    # Progress bars: Kodi scales the fill by control height / background
    # texture height, so background and fill must be equally tall.
    Image.new('RGBA', (16, 8), (255, 255, 255, 255)).save(out('bar_bg.png'))
    gradient_image((256, 8), [VIOLET, CYAN], angle=0).save(out('bar_fill.png'))


def save_slider():
    # Transparent bar (the progress control draws the track) and a 28 px nib;
    # Kodi sizes the nib relative to the bar texture's height.
    Image.new('RGBA', (32, 28), (255, 255, 255, 0)).save(out('slider_bar.png'))
    white_with_alpha(rounded_mask((28, 28), 14)).save(out('slider_nib.png'))


def save_pills():
    white_with_alpha(rounded_mask((128, 76), 38)).save(out('pill.png'))
    # Focus outline drawn right on the button's edge: same 128x76 pill shape
    # and 9-slice border as the fill, so both stretch identically.
    stroke = 5
    outer = rounded_mask((128, 76), 38)
    inner = Image.new('L', (128, 76), 0)
    inner.paste(rounded_mask((128 - 2 * stroke, 76 - 2 * stroke), 38 - stroke), (stroke, stroke))
    white_with_alpha(ImageChops.subtract(outer, inner)).save(out('pill_ring.png'))
    save_ring('ring_focus.png', 256, 16)


GENRE_PAIRS = [
    ((124, 58, 237), (49, 46, 129)), ((37, 99, 235), (12, 74, 110)), ((8, 145, 178), (19, 78, 74)),
    ((5, 150, 105), (20, 83, 45)), ((101, 163, 13), (54, 83, 20)), ((217, 119, 6), (124, 45, 18)),
    ((220, 38, 38), (127, 29, 29)), ((219, 39, 119), (112, 26, 117)), ((147, 51, 234), (88, 28, 135)),
    ((79, 70, 229), (30, 27, 75)), ((13, 148, 136), (22, 78, 99)), ((234, 88, 12), (136, 19, 55)),
]


def save_genre_tiles():
    for index, (light, dark) in enumerate(GENRE_PAIRS):
        tile = gradient_image((256, 256), [light, dark], angle=45)
        add_grain(tile, 5).save(out(f'genre_{index}.png'))


def aura_layer(size, blobs, blur):
    layer = Image.new('RGB', size, BG)
    for (cx, cy, r, color, strength) in blobs:
        blob = Image.new('L', size, 0)
        ImageDraw.Draw(blob).ellipse((cx - r, cy - r, cx + r, cy + r), fill=int(255 * strength))
        blob = blob.filter(ImageFilter.GaussianBlur(blur))
        layer = Image.composite(Image.new('RGB', size, color), layer, blob)
    return layer


def add_grain(img, amount=6):
    rnd = random.Random(7)
    noise = Image.new('L', img.size)
    noise.putdata([128 + rnd.randint(-amount, amount) for _ in range(img.size[0] * img.size[1])])
    return ImageChops.add(img, Image.merge('RGB', (noise, noise, noise)), 1, -128)


def save_background():
    size = (1920, 1080)
    img = aura_layer(size, [
        (1650, -120, 520, VIOLET, 0.32),
        (1880, 520, 380, CYAN, 0.16),
        (-80, 1100, 460, PINK, 0.10),
    ], blur=220)
    add_grain(img, 3).save(out('aura_bg.jpg'), quality=88)


def save_logo():
    """Sidebar logo: the addon icon (your artwork) as a rounded 256 px tile."""
    icon = Image.open(os.path.join(ADDON, 'icon.png')).convert('RGB').resize((256, 256), Image.LANCZOS)
    tile = icon.convert('RGBA')
    tile.putalpha(rounded_mask((256, 256), 56))
    tile.save(out('logo.png'))


def save_placeholders(glyphs):
    for name, glyph, round_shape in (
        ('placeholder_album.png', glyphs['music_note'], False),
        ('placeholder_artist.png', glyphs['person'], True),
        ('placeholder_playlist.png', glyphs['queue_music'], False),
        ('placeholder_radio.png', glyphs['radio'], False),
    ):
        size = 256
        tile = gradient_image((size, size), [(40, 34, 70), (22, 26, 44)], angle=135).convert('RGBA')
        icon = render_icon(glyph, size=110)
        tinted = Image.new('RGBA', icon.size, (255, 255, 255, 0))
        tinted.putalpha(icon.getchannel('A').point(lambda a: int(a * 0.45)))
        tile.alpha_composite(tinted, ((size - 110) // 2, (size - 110) // 2))
        if round_shape:
            tile.putalpha(rounded_mask((size, size), size // 2))
        tile.save(out(name))


def main():
    os.makedirs(MEDIA, exist_ok=True)
    glyphs = load_codepoints()

    for name, glyph_name in ICONS.items():
        glyph = glyphs.get(glyph_name)
        if glyph is None:
            raise SystemExit(f'missing material icon: {glyph_name}')
        render_icon(glyph, name=name).save(out(f'icon_{name}.png'))

    Image.new('RGBA', (8, 8), (255, 255, 255, 255)).save(out('white.png'))
    save_rounded('round_12.png', (48, 48), 12)
    save_rounded('round_20.png', (64, 64), 20)
    save_circle('circle.png', 128)
    save_rounded('mask_round.png', (256, 256), 18)
    save_circle('mask_circle.png', 256)
    save_frame('frame_round.png', 64, 20, 4)
    save_ring('ring.png', 256, 7)
    save_gradients()
    save_glow('glow.png')
    save_shadow('shadow.png')
    save_spinner('spinner.png')
    save_accent()
    save_pills()
    save_slider()
    save_bars()
    save_genre_tiles()
    save_background()
    save_placeholders(glyphs)
    save_logo()  # icon.png and fanart.jpg themselves are hand-made, never overwritten
    print('media written to', MEDIA)


if __name__ == '__main__':
    main()
