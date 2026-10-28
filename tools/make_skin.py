#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 CasX61
"""
Generate Aura-Deck's skin XML (resources/skins/Default/1080i).

Kodi window XML is very repetitive (eight shelves, five button bars, four
song lists), so it is generated from the building blocks below. Control ids
come from resources/lib/ui/ids.py and string ids from tools/i18n.py, the
same sources the Python code uses.

    python3 tools/make_skin.py
"""

import importlib.util
import os
from xml.dom import minidom

from i18n import ADDON, string_id

SKIN = os.path.join(ADDON, 'resources', 'skins', 'Default', '1080i')
ADDON_ID = 'script.auradeck'

_spec = importlib.util.spec_from_file_location('ids', os.path.join(ADDON, 'resources', 'lib', 'ui', 'ids.py'))
ids = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ids)

# Palette (AARRGGBB)
BG = 'FF0B0C14'
CARD = 'FF1C2033'
TEXT = 'FFFFFFFF'
TEXT2 = 'B3FFFFFF'
TEXT3 = '73FFFFFF'
ACCENT = 'FF8B5CF6'
ACCENT2 = 'FF22D3EE'
DARK = 'FF0B0C14'
HOVER = '1FFFFFFF'
FOCUS_ROW = '2EFFFFFF'

# Fonts: Estuary names. Kodi falls back to font13 in skins that lack one.
F_SMALL = 'font10'
F_BODY = 'font12'
F_ITEM = 'font13'
F_LARGE = 'font14'
F_H3 = 'font25_title'
F_H2 = 'font30_title'
F_H1 = 'font45'
F_LYRIC = 'font32'
F_LYRIC_NOW = 'font45_title'
F_LYRIC_NOW_LONG = 'font32_title'   # current line too long for two lines of F_LYRIC_NOW

# Layout
CX = 150            # content left edge (right of the collapsed sidebar)
CW = 1710           # content width
MINI_Y = 976        # mini player top
ROW = ids.TRACK_ROW_HEIGHT
HERO_HEIGHT = {'home': 330, 'artist': 610, 'search': 390}

# Kodi conditions can't compare two infolabels, so Python flags the playing row.
PLAYING = 'String.IsEqual(ListItem.Property(playing),1)'


def S(key):
    return f'$ADDON[{ADDON_ID} {string_id(key)}]'


def prop(name):
    return f'$INFO[Window.Property({name})]'


def view_is(name):
    return f'String.IsEqual(Window.Property(view),{name})'


def kind_is(kind):
    return f'String.IsEqual(ListItem.Property(kind),{kind})'


def has_items(list_id):
    return f'Integer.IsGreater(Container({list_id}).NumItems,0)'


# Primitive controls
def _visible(condition):
    return f'<visible>{condition}</visible>' if condition else ''


ROUND_TEXTURES = ('circle.png', 'btn_accent.png', 'ring.png', 'ring_focus.png', 'spinner.png', 'glow.png', 'logo.png',
                  'slider_nib.png')


def keeps_shape(texture):
    """
    Circles and icons must stay round when Kodi stretches the 16:9 skin onto a
    screen of another shape (e.g. a 16:10 laptop), so they keep their aspect.
    """
    return texture in ROUND_TEXTURES or texture.startswith('icon_') or 'Property(icon)' in texture


def image(x, y, w, h, texture, color=None, visible=None, aspect=None, diffuse=None,
          fallback=None, background=False, border=None, fade=None, extra=''):
    if aspect is None and keeps_shape(texture):
        aspect = 'keep'
    attrs = ''
    if diffuse:
        attrs += f' diffuse="{diffuse}"'
    if fallback:
        attrs += f' fallback="{fallback}"'
    if background:
        attrs += ' background="true"'
    if border:
        attrs += f' border="{border}"'
    return (f'<control type="image"><left>{x}</left><top>{y}</top><width>{w}</width><height>{h}</height>'
            f'<texture{attrs}>{texture}</texture>'
            + (f'<colordiffuse>{color}</colordiffuse>' if color else '')
            + (f'<aspectratio>{aspect}</aspectratio>' if aspect else '')
            + (f'<fadetime>{fade}</fadetime>' if fade else '')
            + _visible(visible) + extra + '</control>')


def label(x, y, w, h, text, font=F_ITEM, color=TEXT, align='left', aligny='center',
          visible=None, scroll=False, wrap=False, extra=''):
    return (f'<control type="label"><left>{x}</left><top>{y}</top><width>{w}</width><height>{h}</height>'
            f'<font>{font}</font><textcolor>{color}</textcolor><align>{align}</align><aligny>{aligny}</aligny>'
            f'<label>{text}</label>'
            + ('<scroll>true</scroll>' if scroll else '')
            + ('<wrapmultiline>true</wrapmultiline>' if wrap else '')
            + _visible(visible) + extra + '</control>')


def group(content, x=0, y=0, w=None, h=None, visible=None, control_id=None, extra=''):
    size = (f'<width>{w}</width>' if w is not None else '') + (f'<height>{h}</height>' if h is not None else '')
    cid = f' id="{control_id}"' if control_id else ''
    return (f'<control type="group"{cid}><left>{x}</left><top>{y}</top>{size}'
            + _visible(visible) + extra + content + '</control>')


def nav(**directions):
    """onup/ondown/... tags; a value may be a list of (condition, target)."""
    out = ''
    for direction, target in directions.items():
        if target is None:
            continue
        if isinstance(target, list):
            out += ''.join(f'<{direction} condition="{cond}">{dest}</{direction}>' for cond, dest in target)
        else:
            out += f'<{direction}>{target}</{direction}>'
    return out


def zoom(list_id, amount=105, center='auto'):
    return (f'<animation effect="zoom" start="100" end="{amount}" center="{center}" time="200" '
            f'tween="sine" easing="out" condition="Control.HasFocus({list_id})">Conditional</animation>')


# Building blocks
def song_row(list_id, width, focused, album_column=False):
    """One row of any song list: cover or track number, title/artist, icons, duration."""
    is_song = kind_is('song') + '|' + kind_is('radio')
    has_focus = f'Control.HasFocus({list_id})'
    parts = []
    if focused:
        parts.append(image(0, 4, width, ROW - 8, 'round_12.png', FOCUS_ROW, visible=has_focus, border=12))
    # Cover or number
    parts.append(image(14, 10, ROW - 20, ROW - 20, '$INFO[ListItem.Art(thumb)]', diffuse='mask_round.png',
                       fallback='placeholder_album.png', background=True, aspect='scale',
                       visible=f'[{is_song}] + String.IsEqual(ListItem.Property(cover),1)'))
    parts.append(image(14, 10, ROW - 20, ROW - 20, 'white.png', 'B30B0C14', diffuse='mask_round.png',
                       visible=f'String.IsEqual(ListItem.Property(cover),1) + {PLAYING}'))
    parts.append(label(14, 0, ROW - 20, ROW, '$INFO[ListItem.Property(number)]', F_BODY, TEXT3, 'center',
                       visible=f'{kind_is("song")} + !String.IsEqual(ListItem.Property(cover),1) + !{PLAYING}'))
    parts.append(image(14 + (ROW - 20 - 36) // 2, (ROW - 36) // 2, 36, 36, 'icon_equalizer.png', ACCENT2,
                       visible=PLAYING,
                       extra='<animation effect="fade" start="100" end="45" time="700" pulse="true" '
                             'condition="true">Conditional</animation>'))
    # Title and artist
    text_x = ROW + 8
    right = 300 if album_column else 210
    title_w = width - text_x - right - (420 if album_column else 0)
    parts.append(label(text_x, 10, title_w, 34, '$INFO[ListItem.Label]', F_ITEM, TEXT,
                       visible=f'[{is_song}] + !{PLAYING}', scroll=focused))
    parts.append(label(text_x, 10, title_w, 34, '$INFO[ListItem.Label]', F_ITEM, ACCENT2,
                       visible=f'[{is_song}] + {PLAYING}', scroll=focused))
    parts.append(label(text_x, 44, title_w, 28, '$INFO[ListItem.Label2]', F_SMALL, TEXT2, visible=is_song))
    if album_column:
        parts.append(label(width - right - 400, 0, 380, ROW, '$INFO[ListItem.Property(album)]', F_BODY, TEXT2,
                           visible=kind_is('song')))
    # Status icons and duration
    parts.append(image(width - 196, (ROW - 28) // 2, 28, 28, 'icon_favourite.png', ACCENT,
                       visible='String.IsEqual(ListItem.Property(starred),1)'))
    parts.append(image(width - 156, (ROW - 28) // 2, 28, 28, 'icon_downloaded.png', TEXT2,
                       visible='String.IsEqual(ListItem.Property(offline),1)'))
    parts.append(label(width - 120, 0, 100, ROW, '$INFO[ListItem.Property(duration)]', F_BODY, TEXT2, 'right',
                       visible=kind_is('song')))
    # Disc separator and "show all"
    parts.append(label(18, 18, width - 40, ROW - 18, '$INFO[ListItem.Label]', F_BODY, ACCENT2,
                       visible=kind_is('separator')))
    parts.append(image(18, (ROW - 32) // 2, 32, 32, 'icon_arrow.png', ACCENT2, visible=kind_is('more')))
    parts.append(label(66, 0, width - 100, ROW, '$INFO[ListItem.Label]', F_ITEM, ACCENT2, visible=kind_is('more')))
    return ''.join(parts)


def song_list(list_id, x, y, w, h, navigation, album_column=False, control_type='list'):
    return (f'<control type="{control_type}" id="{list_id}"><left>{x}</left><top>{y}</top>'
            f'<width>{w}</width><height>{h}</height><orientation>vertical</orientation>'
            + navigation +
            '<scrolltime tween="cubic" easing="out">250</scrolltime>'
            f'<itemlayout width="{w}" height="{ROW}">{song_row(list_id, w, False, album_column)}</itemlayout>'
            f'<focusedlayout width="{w}" height="{ROW}">{song_row(list_id, w, True, album_column)}</focusedlayout>'
            '</control>')


def card(list_id, size, focused):
    """Cover card for albums, artists, playlists, genres and 'show all'."""
    has_focus = f'Control.HasFocus({list_id})'
    round_kind = kind_is('artist')
    square = f'!{round_kind} + !{kind_is("more")}'
    pad = 14
    inner = []
    if focused:
        inner.append(image(-50, -40, size + 100, size + 100, 'glow.png', '998B5CF6', visible=has_focus))
    inner.append(image(0, 0, size, size, '$INFO[ListItem.Art(thumb)]', diffuse='mask_round.png',
                       fallback='placeholder_album.png', background=True, aspect='scale', visible=square))
    inner.append(image(0, 0, size, size, '$INFO[ListItem.Art(thumb)]', diffuse='mask_circle.png',
                       fallback='placeholder_artist.png', background=True, aspect='keep', visible=round_kind))
    # Genre tiles: an album cover of the genre, tinted with the genre's colour,
    # and the name on a dark fade at the bottom
    genre = kind_is('genre')
    inner.append(image(0, 0, size, size, '$INFO[ListItem.Property(tile)]', 'A6FFFFFF', diffuse='mask_round.png',
                       visible=genre))
    inner.append(image(0, size // 2, size, size // 2, 'grad_v.png', 'B3000000', visible=genre))
    inner.append(label(18, size - 62, size - 36, 44, '$INFO[ListItem.Label]', F_H3, TEXT, visible=genre))
    # "Show all" tile
    inner.append(image(0, 0, size, size, 'mask_round.png', CARD, visible=kind_is('more')))
    inner.append(image(size // 2 - 36, size // 2 - 56, 72, 72, 'icon_arrow.png', ACCENT2, visible=kind_is('more')))
    inner.append(label(0, size // 2 + 30, size, 40, '$INFO[ListItem.Label]', F_BODY, TEXT, 'center',
                       visible=kind_is('more')))
    if focused:
        inner.append(image(-6, -6, size + 12, size + 12, 'frame_round.png', TEXT, border=20,
                           visible=f'{has_focus} + !{round_kind}'))
        inner.append(image(-6, -6, size + 12, size + 12, 'ring.png', TEXT, visible=f'{has_focus} + {round_kind}'))
    cover = group(''.join(inner), pad, pad, size, size, extra=zoom(list_id) if focused else '')

    text_visible = f'!{kind_is("genre")} + !{kind_is("more")}'
    align = 'left'
    labels = (
        label(pad, pad + size + 12, size, 34, '$INFO[ListItem.Label]', F_BODY, TEXT, align,
              visible=f'{text_visible} + !{round_kind}', scroll=focused)
        + label(pad, pad + size + 12, size, 34, '$INFO[ListItem.Label]', F_BODY, TEXT, 'center',
                visible=f'{text_visible} + {round_kind}', scroll=focused)
        + label(pad, pad + size + 46, size, 30, '$INFO[ListItem.Label2]', F_SMALL, TEXT2, align,
                visible=f'{text_visible} + !{round_kind}')
        + label(pad, pad + size + 46, size, 30, '$INFO[ListItem.Label2]', F_SMALL, TEXT2, 'center',
                visible=f'{text_visible} + {round_kind}')
    )
    return cover + labels


def shelf_list(list_id, size=250):
    item_w, item_h = size + 40, size + 110
    return (f'<control type="list" id="{list_id}"><left>0</left><top>0</top>'
            f'<width>{CW + 40}</width><height>{item_h}</height><orientation>horizontal</orientation>'
            + nav(onleft=ids.SIDEBAR) +
            '<scrolltime tween="cubic" easing="out">300</scrolltime>'
            f'<itemlayout width="{item_w}" height="{item_h}">{card(list_id, size, False)}</itemlayout>'
            f'<focusedlayout width="{item_w}" height="{item_h}">{card(list_id, size, True)}</focusedlayout>'
            '</control>')


PILL_W = 320


BAR_PAD_X = 16   # room inside a bar's list for focus rings and zoom, which
BAR_PAD_Y = 10   # Kodi would otherwise clip at the list's edge


def _pill_layout(list_id, focused):
    """Text pill with icon; 'primary' items get the gradient fill."""
    has_focus = f'Control.HasFocus({list_id})' if focused else 'false'
    primary = 'String.IsEqual(ListItem.Property(style),primary)'
    inverted = f'!{primary} + {has_focus}'      # plain pill with focus: white fill, dark text
    content = (
        image(0, 4, PILL_W, 76, 'btn_primary.png', border='38,0,38,0', visible=primary)
        + image(0, 4, PILL_W, 76, 'pill.png', HOVER, border='40,0,40,0', visible=f'!{primary} + !{has_focus}')
        + image(0, 4, PILL_W, 76, 'pill.png', TEXT, border='40,0,40,0', visible=inverted)
        + image(0, 4, PILL_W, 76, 'pill_ring.png', TEXT, border='38,0,38,0', visible=f'{primary} + {has_focus}')
        + image(26, 24, 36, 36, '$INFO[ListItem.Property(icon)]', TEXT, visible=f'![{inverted}]')
        + image(26, 24, 36, 36, '$INFO[ListItem.Property(icon)]', DARK, visible=inverted)
        + label(72, 4, PILL_W - 92, 76, '$INFO[ListItem.Label]', F_BODY, TEXT, visible=f'![{inverted}]',
                scroll=focused)
        + label(72, 4, PILL_W - 92, 76, '$INFO[ListItem.Label]', F_BODY, DARK, visible=inverted, scroll=focused)
    )
    return group(content, BAR_PAD_X, BAR_PAD_Y, PILL_W, 84, extra=zoom(list_id, 103) if focused else '')


def _round_layout(list_id, focused):
    """Round icon button; 'accent' items get the gradient fill."""
    has_focus = f'Control.HasFocus({list_id})' if focused else 'false'
    accent = 'String.IsEqual(ListItem.Property(style),accent)'
    inverted = f'!{accent} + {has_focus}'
    return group(
        image(0, 4, 76, 76, 'btn_accent.png', visible=accent)
        + image(0, 4, 76, 76, 'ring_focus.png', TEXT, visible=f'{accent} + {has_focus}')
        + image(0, 4, 76, 76, 'circle.png', HOVER, visible=f'!{accent} + !{has_focus}')
        + image(0, 4, 76, 76, 'circle.png', TEXT, visible=inverted)
        + image(18, 22, 40, 40, '$INFO[ListItem.Property(icon)]', TEXT, visible=f'![{inverted}]')
        + image(18, 22, 40, 40, '$INFO[ListItem.Property(icon)]', DARK, visible=inverted),
        BAR_PAD_X, BAR_PAD_Y, 76, 84)


def button_bar(list_id, x, y, w, navigation, round_buttons=False):
    """
    A horizontal bar of buttons filled from Python. Kodi picks item layouts
    per list, not per item, so each bar has one shape: text pills, or round
    icons with the focused button's label shown underneath.
    """
    width = 94 if round_buttons else PILL_W + 14
    layout = _round_layout if round_buttons else _pill_layout
    xml = (f'<control type="list" id="{list_id}"><left>{x - BAR_PAD_X}</left><top>{y - BAR_PAD_Y}</top>'
           f'<width>{w + BAR_PAD_X}</width><height>{84 + 2 * BAR_PAD_Y}</height>'
           '<orientation>horizontal</orientation>' + navigation +
           '<scrolltime>200</scrolltime>'
           f'<itemlayout width="{width}" height="{84 + 2 * BAR_PAD_Y}">{layout(list_id, False)}</itemlayout>'
           f'<focusedlayout width="{width}" height="{84 + 2 * BAR_PAD_Y}">{layout(list_id, True)}</focusedlayout>'
           '</control>')
    if round_buttons:
        xml += label(x, y + 88, 600, 30, f'$INFO[Container({list_id}).ListItem.Label]', F_SMALL, TEXT2,
                     visible=f'Control.HasFocus({list_id})')
    return xml


# Main window
def background():
    return (
        image(0, 0, 1920, 1080, 'aura_bg.jpg')
        # Album / playlist: the cover as a soft colour wash
        + image(0, 0, 1920, 1080, prop('backdrop'), '1AFFFFFF', aspect='scale', fade=400, background=True,
                visible=f'{view_is("detail")} + !String.IsEmpty(Window.Property(backdrop))')
        + image(0, 0, 1920, 1080, 'grad_v.png', 'E60B0C14', visible=view_is('detail'))
        # Artist: the picture on the right, fading into the background
        + group(
            image(0, 0, 1180, 760, prop('backdrop'), 'CCFFFFFF', aspect='scale', fade=500, background=True)
            + image(0, 0, 520, 760, 'grad_h.png', BG)
            + image(0, 300, 1180, 460, 'grad_v.png', BG),
            x=740, y=0,
            visible=f'{view_is("rows")} + String.IsEqual(Window.Property(hero),artist) + '
                    '!String.IsEmpty(Window.Property(backdrop))')
        # Dim the picture while browsing the shelves below it. An overlay, not a
        # fade of the group: fading would also thin out the gradients and leave
        # the picture's edges hard.
        + image(0, 0, 1920, 1080, 'white.png', 'A60B0C14',
                visible=f'{view_is("rows")} + String.IsEqual(Window.Property(hero),artist) + '
                        'ControlGroup(1000).HasFocus(0)',
                extra='<animation effect="fade" time="300">VisibleChange</animation>')
    )


def hero_home():
    height = HERO_HEIGHT['home']
    return group(
        label(0, 80, CW, 90, prop('hero.title'), F_H1, TEXT)
        + label(0, 168, CW, 40, prop('hero.subtitle'), F_ITEM, TEXT2)
        + button_bar(ids.HERO_BUTTONS, -6, 222, CW, nav(onleft=ids.SIDEBAR, ondown=ids.ROWS)),
        x=CX, y=0, w=CW, h=height,
        visible='String.IsEqual(Window.Property(hero),home)')


def hero_artist():
    height = HERO_HEIGHT['artist']
    return group(
        label(0, 120, 900, 34, S('nav_artists'), F_BODY, ACCENT2)
        + label(0, 152, 1100, 100, prop('artist.name'), F_H1, TEXT, scroll=True)
        + label(0, 254, 1100, 40, prop('artist.meta'), F_BODY, TEXT2)
        + '<control type="textbox"><left>0</left><top>304</top><width>1000</width><height>170</height>'
          f'<font>{F_BODY}</font><textcolor>{TEXT2}</textcolor><label>{prop("artist.bio")}</label>'
          '<autoscroll delay="6000" time="3000" repeat="10000">false</autoscroll></control>'
        + button_bar(ids.ARTIST_BUTTONS, -6, 494, CW, nav(onleft=ids.SIDEBAR, ondown=ids.ROWS)),
        x=CX, y=0, w=CW, h=height,
        visible='String.IsEqual(Window.Property(hero),artist)')


def hero_search():
    height = HERO_HEIGHT['search']
    field_focus = f'Control.HasFocus({ids.SEARCH_FIELD})'
    field = (
        f'<control type="button" id="{ids.SEARCH_FIELD}"><left>0</left><top>170</top><width>1100</width>'
        '<height>92</height>'
        f'<texturefocus border="20" colordiffuse="{TEXT}">round_20.png</texturefocus>'
        f'<texturenofocus border="20" colordiffuse="{CARD}">round_20.png</texturenofocus>'
        f'<label>{prop("search.query")}</label><font>{F_LARGE}</font>'
        f'<textcolor>{TEXT2}</textcolor><focusedcolor>{DARK}</focusedcolor>'
        '<textoffsetx>96</textoffsetx><aligny>center</aligny>'
        + nav(onleft=ids.SIDEBAR, ondown=ids.SEARCH_HISTORY) + '</control>'
        + image(32, 196, 40, 40, 'icon_search.png', TEXT2, visible=f'!{field_focus}')
        + image(32, 196, 40, 40, 'icon_search.png', DARK, visible=field_focus)
    )
    history = (
        f'<control type="list" id="{ids.SEARCH_HISTORY}"><left>-4</left><top>286</top><width>{CW}</width>'
        '<height>70</height><orientation>horizontal</orientation>'
        + nav(onleft=ids.SIDEBAR, onup=ids.SEARCH_FIELD, ondown=ids.ROWS) +
        '<scrolltime>200</scrolltime>'
        '<itemlayout width="290" height="70">'
        + image(4, 4, 270, 60, 'pill.png', HOVER, border='32,0,32,0')
        + image(24, 20, 30, 30, 'icon_history.png', TEXT3)
        + label(64, 4, 196, 60, '$INFO[ListItem.Label]', F_BODY, TEXT2)
        + '</itemlayout><focusedlayout width="290" height="70">'
        + image(4, 4, 270, 60, 'pill.png', HOVER, border='32,0,32,0',
                visible=f'!Control.HasFocus({ids.SEARCH_HISTORY})')
        + image(4, 4, 270, 60, 'pill.png', TEXT, border='32,0,32,0',
                visible=f'Control.HasFocus({ids.SEARCH_HISTORY})')
        + image(24, 20, 30, 30, 'icon_history.png', TEXT3)
        + label(64, 4, 196, 60, '$INFO[ListItem.Label]', F_BODY, TEXT2,
                visible=f'!Control.HasFocus({ids.SEARCH_HISTORY})')
        + label(64, 4, 196, 60, '$INFO[ListItem.Label]', F_BODY, DARK,
                visible=f'Control.HasFocus({ids.SEARCH_HISTORY})', scroll=True)
        + '</focusedlayout></control>'
    )
    return group(
        label(0, 70, CW, 90, S('nav_search'), F_H1, TEXT) + field + history,
        x=CX, y=0, w=CW, h=height,
        visible='String.IsEqual(Window.Property(hero),search)')


def rows_view():
    hero_focus_away = 'ControlGroup(1000).HasFocus(0)'
    heroes = group(
        hero_home() + hero_artist() + hero_search(),
        extra=('<animation effect="fade" start="100" end="0" time="200" '
               f'condition="{hero_focus_away}">Conditional</animation>'
               '<animation effect="slide" end="0,-140" time="300" tween="cubic" easing="out" '
               f'condition="{hero_focus_away}">Conditional</animation>'))

    children = [
        f'<control type="label" id="{ids.TRACKS_SHELF_LABEL}"><width>{CW}</width><height>70</height>'
        f'<font>{F_H3}</font><textcolor>{TEXT}</textcolor><aligny>center</aligny>'
        f'<label>{prop("tracks.title")}</label>{_visible(has_items(ids.TRACKS_SHELF))}</control>',
        song_list(ids.TRACKS_SHELF, 0, 0, CW - 40, ROW * 7, nav(onleft=ids.SIDEBAR))
        .replace('<orientation>vertical</orientation>',
                 f'<orientation>vertical</orientation>{_visible(has_items(ids.TRACKS_SHELF))}', 1),
    ]
    for index in range(ids.SHELF_COUNT):
        list_id = ids.shelf(index)
        children.append(
            f'<control type="label" id="{ids.shelf_label(index)}"><width>{CW}</width><height>56</height>'
            f'<font>{F_H3}</font><textcolor>{TEXT}</textcolor><aligny>center</aligny>'
            f'<label>{prop(f"shelf{index}.title")}</label>{_visible(has_items(list_id))}</control>')
        children.append(shelf_list(list_id).replace(
            '<orientation>horizontal</orientation>',
            f'<orientation>horizontal</orientation>{_visible(has_items(list_id))}', 1))

    grouplist = (
        f'<control type="grouplist" id="{ids.ROWS}"><left>{CX}</left><top>30</top>'
        f'<width>{CW + 60}</width><height>{MINI_Y - 30}</height><orientation>vertical</orientation>'
        '<itemgap>6</itemgap><scrolltime tween="cubic" easing="out">320</scrolltime>'
        + nav(onup=ids.TOP_ROUTER, ondown=ids.MINI_OPEN, onleft=ids.SIDEBAR)
        + ''.join(children) + '</control>')

    slides = ''.join(
        f'<animation effect="slide" end="0,{height - 20}" time="320" tween="cubic" easing="out" '
        f'condition="String.IsEqual(Window.Property(hero),{name}) + !{hero_focus_away}">Conditional</animation>'
        for name, height in HERO_HEIGHT.items())
    body = group(grouplist, extra=slides)
    return group(heroes + body, visible=view_is('rows'))


def page_header(button_list):
    return (
        label(CX, 34, CW, 90, prop('page.title'), F_H1, TEXT)
        + label(CX, 116, CW, 40, prop('page.subtitle'), F_BODY, TEXT2)
        + button_bar(button_list, CX - 6, 164, CW,
                     nav(onleft=ids.SIDEBAR, ondown=ids.GRID if button_list == ids.GRID_BUTTONS else ids.TRACKLIST))
    )


def grid_view():
    size, item_w, item_h = 234, 285, 350
    panel = (
        f'<control type="panel" id="{ids.GRID}"><left>{CX - 14}</left><top>262</top>'
        f'<width>{CW + 30}</width><height>{item_h * 2}</height><orientation>vertical</orientation>'
        + nav(onup=ids.GRID_BUTTONS, onleft=ids.SIDEBAR, ondown=ids.MINI_OPEN) +
        '<scrolltime tween="cubic" easing="out">300</scrolltime>'
        f'<itemlayout width="{item_w}" height="{item_h}">{card(ids.GRID, size, False)}</itemlayout>'
        f'<focusedlayout width="{item_w}" height="{item_h}">{card(ids.GRID, size, True)}</focusedlayout>'
        '</control>')
    return group(page_header(ids.GRID_BUTTONS) + panel, visible=view_is('grid'))


def tracks_view():
    songs = song_list(ids.TRACKLIST, CX, 270, CW, ROW * 8,
                      nav(onup=ids.TRACKLIST_BUTTONS, onleft=ids.SIDEBAR, ondown=ids.MINI_OPEN),
                      album_column=True)
    return group(page_header(ids.TRACKLIST_BUTTONS) + songs, visible=view_is('tracks'))


def detail_view():
    cover = 460
    column = (
        image(-90, -40, cover + 180, cover + 180, 'glow.png', '808B5CF6')
        + image(-24, -14, cover + 48, cover + 56, 'shadow.png', border=40)
        + image(0, 0, cover, cover, prop('detail.cover'), diffuse='mask_round.png',
                fallback='placeholder_album.png', aspect='scale', background=True, fade=300)
        # Bottom-aligned: one- and two-line titles both sit right above the artist
        + label(0, cover + 30, 600, 60, prop('detail.title'), F_H2, TEXT, scroll=True)
        + label(0, cover + 92, 600, 40, prop('detail.artist'), F_ITEM, ACCENT2)
        + label(0, cover + 134, 600, 32, prop('detail.meta'), F_SMALL, TEXT2)
        + label(0, cover + 166, 600, 32, prop('detail.meta2'), F_SMALL, TEXT3)
    )
    buttons = button_bar(ids.DETAIL_BUTTONS, CX - 6, 64 + cover + 218, 600,
                         nav(onleft=ids.SIDEBAR, onright=ids.DETAIL_TRACKS, ondown=ids.DETAIL_TRACKS),
                         round_buttons=True)
    tracks = song_list(ids.DETAIL_TRACKS, CX + 640, 50, CW - 640, ROW * 11,
                       nav(onleft=ids.DETAIL_BUTTONS, ondown=ids.MINI_OPEN))
    return group(group(column, CX, 64) + buttons + tracks, visible=view_is('detail'))


def overlays():
    return (
        label(CX, 640, CW, 120, prop('empty'), F_ITEM, TEXT2, 'center', wrap=True,
              visible='!String.IsEmpty(Window.Property(empty))')
        + image(CX + CW // 2 - 40, 520, 80, 80, 'spinner.png', ACCENT2,
                visible='!String.IsEmpty(Window.Property(busy))',
                extra='<animation effect="rotate" end="-360" center="auto" time="900" loop="true" '
                      'condition="true">Conditional</animation>'
                      '<animation effect="fade" start="0" end="100" time="200" delay="300">Visible</animation>')
    )


def mini_player():
    up = ids.ENTRY_ROUTER

    def round_button(control_id, x, icon_xml, action, left, right):
        focus = f'Control.HasFocus({control_id})'
        return (image(x, MINI_Y + 16, 72, 72, 'circle.png', HOVER, visible=f'!{focus}')
                + image(x, MINI_Y + 16, 72, 72, 'circle.png', ACCENT, visible=focus)
                + f'<control type="button" id="{control_id}"><left>{x}</left><top>{MINI_Y + 16}</top>'
                '<width>72</width><height>72</height><texturefocus></texturefocus><texturenofocus></texturenofocus>'
                f'<label></label><onclick>{action}</onclick>'
                + nav(onup=up, onleft=left, onright=right) + '</control>' + icon_xml)

    icon = lambda x, name, visible=None: image(x + 18, MINI_Y + 34, 36, 36, name, TEXT, visible=visible)
    controls = (
        image(0, MINI_Y, 1920, 1080 - MINI_Y, 'white.png', 'F20E101B')
        + image(0, MINI_Y, 1920, 1, 'white.png', '1AFFFFFF')
        + '<control type="progress"><left>0</left><top>' + str(MINI_Y) + '</top><width>1920</width>'
          '<height>4</height><texturebg colordiffuse="14FFFFFF">bar_bg.png</texturebg>'
          '<midtexture>bar_fill.png</midtexture><info>Player.Progress</info></control>'
        + f'<control type="button" id="{ids.MINI_OPEN}"><left>{CX - 20}</left><top>{MINI_Y + 10}</top>'
          '<width>1180</width><height>84</height>'
          f'<texturefocus border="12" colordiffuse="{FOCUS_ROW}">round_12.png</texturefocus>'
          '<texturenofocus></texturenofocus><label></label>'
        + nav(onup=up, onleft=ids.SIDEBAR, onright=ids.MINI_PREV) + '</control>'
        + image(CX, MINI_Y + 18, 68, 68, '$INFO[Player.Art(thumb)]', diffuse='mask_round.png',
                fallback='placeholder_album.png', aspect='scale', background=True)
        + label(CX + 88, MINI_Y + 16, 900, 38, '$INFO[MusicPlayer.Title]', F_ITEM, TEXT, scroll=True)
        + label(CX + 88, MINI_Y + 52, 900, 32, '$INFO[MusicPlayer.Artist]', F_SMALL, TEXT2)
        + label(1300, MINI_Y + 16, 300, 72, '$INFO[Player.Time] / $INFO[Player.Duration]', F_SMALL, TEXT2, 'right')
        + round_button(ids.MINI_PREV, 1640, icon(1640, 'icon_prev.png'), 'PlayerControl(Previous)',
                       ids.MINI_OPEN, ids.MINI_PLAY)
        + round_button(ids.MINI_PLAY, 1724, icon(1724, 'icon_pause.png', '!Player.Paused')
                       + icon(1724, 'icon_play.png', 'Player.Paused'), 'PlayerControl(Play)',
                       ids.MINI_PREV, ids.MINI_NEXT)
        + round_button(ids.MINI_NEXT, 1808, icon(1808, 'icon_next.png'), 'PlayerControl(Next)',
                       ids.MINI_PLAY, None)
    )
    return group(controls, visible='Player.HasAudio',
                 extra='<animation effect="slide" start="0,120" end="0,0" time="300" tween="cubic" '
                       'easing="out">Visible</animation>')


def sidebar():
    has_focus = f'Control.HasFocus({ids.SIDEBAR})'
    active = 'String.IsEqual(ListItem.Property(active),1)'

    def entry(focused):
        on = f'{has_focus}' if focused else 'false'
        return (
            (image(16, 8, 348, 64, 'round_20.png', TEXT, border=20, visible=on) if focused else '')
            + image(0, 20, 5, 40, 'white.png', ACCENT2, visible=f'{active} + !{on}')
            + image(35, 20, 40, 40, '$INFO[ListItem.Property(icon)]', ACCENT2, visible=f'{active} + !{on}')
            + image(35, 20, 40, 40, '$INFO[ListItem.Property(icon)]', TEXT2, visible=f'!{active} + !{on}')
            + image(35, 20, 40, 40, '$INFO[ListItem.Property(icon)]', DARK, visible=on)
            + label(100, 0, 250, 80, '$INFO[ListItem.Label]', F_ITEM, TEXT, visible=f'{has_focus} + !{on}')
            + label(100, 0, 250, 80, '$INFO[ListItem.Label]', F_ITEM, DARK, visible=on)
        )

    collapsed = image(0, 0, 110, 1080, 'white.png', 'D90C0E18', visible=f'!{has_focus}')
    expanded = group(
        image(0, 0, 380, 1080, 'white.png', 'F70C0E18')
        + image(380, 0, 160, 1080, 'grad_h.png', '99000000')
        + label(100, 40, 260, 60, 'Aura-Deck', F_LARGE, TEXT),
        visible=has_focus,
        extra='<animation effect="fade" time="180">VisibleChange</animation>'
              '<animation effect="slide" start="-120,0" end="0,0" time="220" tween="cubic" easing="out">'
              'Visible</animation>')
    menu = (
        f'<control type="list" id="{ids.SIDEBAR}"><left>0</left><top>150</top><width>380</width>'
        f'<height>820</height><orientation>vertical</orientation>'
        + nav(onright=ids.ENTRY_ROUTER, ondown=ids.MINI_OPEN) +
        '<scrolltime>150</scrolltime>'
        f'<itemlayout width="380" height="80">{entry(False)}</itemlayout>'
        f'<focusedlayout width="380" height="80">{entry(True)}</focusedlayout>'
        '</control>')
    return collapsed + expanded + image(27, 40, 56, 56, 'logo.png') + menu


def routers():
    """1 px invisible buttons Python forwards focus from (see ids.ROUTERS)."""
    return ''.join(
        f'<control type="button" id="{control_id}"><left>{index}</left><top>0</top><width>1</width><height>1</height>'
        '<texturefocus></texturefocus><texturenofocus></texturenofocus><label></label></control>'
        for index, control_id in enumerate(ids.ROUTERS))


def main_window():
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<!-- SPDX-License-Identifier: GPL-3.0-or-later. Generated by tools/make_skin.py - edit the generator, not this file. -->\n'
            f'<window><defaultcontrol always="true">{ids.SIDEBAR}</defaultcontrol><controls>'
            + background() + rows_view() + grid_view() + tracks_view() + detail_view()
            + overlays() + mini_player() + sidebar() + routers()
            + '</controls></window>\n')


# Now playing dialog
def now_playing():
    left, cover = 140, 620
    panel_lyrics = 'String.IsEqual(Window.Property(panel),lyrics)'
    panel_queue = 'String.IsEqual(Window.Property(panel),queue)'
    lyrics_state = lambda state: f'String.IsEqual(Window.Property(lyrics),{state})'
    has_lyrics = f'[{lyrics_state("synced")} | {lyrics_state("plain")}]'
    to_panel = [(panel_lyrics, ids.NP_LYRICS), (panel_queue, ids.NP_QUEUE)]
    to_tab = [(panel_lyrics, ids.NP_TAB_LYRICS), (panel_queue, ids.NP_TAB_QUEUE)]

    background_xml = (
        image(0, 0, 1920, 1080, 'aura_bg.jpg')
        + image(0, 0, 1920, 1080, '$INFO[Player.Art(fanart)]', '38FFFFFF', aspect='scale', fade=600,
                background=True)
        + image(0, 0, 1920, 1080, '$INFO[Player.Art(thumb)]', '1FFFFFFF', aspect='scale', fade=600,
                background=True, visible='String.IsEmpty(Player.Art(fanart))')
        + image(0, 0, 1920, 1080, 'grad_h.png', 'B30B0C14')
        + image(0, 380, 1920, 700, 'grad_v.png', 'E60B0C14')
    )

    artwork = (
        image(left - 110, 0, cover + 220, cover + 220, 'glow.png', 'A68B5CF6',
              extra='<animation effect="fade" start="100" end="60" time="2400" pulse="true" '
                    'condition="!Player.Paused">Conditional</animation>')
        + image(left - 30, 70, cover + 60, cover + 70, 'shadow.png', border=40)
        + image(left, 90, cover, cover, '$INFO[Player.Art(thumb)]', diffuse='mask_round.png',
                fallback='placeholder_album.png', aspect='scale', background=True, fade=300,
                extra='<animation effect="zoom" end="96" center="auto" time="400" tween="cubic" easing="out" '
                      'condition="Player.Paused">Conditional</animation>')
    )

    meta = (
        label(left, 734, cover, 60, '$INFO[MusicPlayer.Title]', F_H2, TEXT, scroll=True)
        + label(left, 794, cover, 44, '$INFO[MusicPlayer.Artist]', F_LARGE, ACCENT2, scroll=True)
        + label(left, 838, cover, 36, '$INFO[MusicPlayer.Album]', F_BODY, TEXT2, scroll=True)
    )

    progress = (
        f'<control type="progress"><left>{left}</left><top>{895}</top><width>{cover}</width><height>6</height>'
        '<texturebg colordiffuse="26FFFFFF">bar_bg.png</texturebg>'
        '<midtexture>bar_fill.png</midtexture><info>Player.Progress</info></control>'
        + f'<control type="slider" id="{ids.NP_SLIDER}"><left>{left - 14}</left><top>{884}</top>'
          f'<width>{cover + 28}</width><height>28</height>'
          # Kodi scales the nib by height / bar texture height: both are 28 px.
          '<texturesliderbar>slider_bar.png</texturesliderbar>'
          '<textureslidernib colordiffuse="00FFFFFF">slider_nib.png</textureslidernib>'
          '<textureslidernibfocus colordiffuse="FFFFFFFF">slider_nib.png</textureslidernibfocus>'
          '<info>Player.Progress</info><action>seek</action><orientation>horizontal</orientation>'
        + nav(ondown=ids.NP_PLAY, onright=to_tab) + '</control>'
        + label(left, 914, 200, 30, '$INFO[Player.Time]', F_SMALL, TEXT2)
        + label(left + cover - 200, 914, 200, 30, '$INFO[Player.Duration]', F_SMALL, TEXT2, 'right')
    )

    buttons = []
    layout = [
        (ids.NP_SHUFFLE, 'PlayerControl(Random)', [('icon_shuffle.png', '!Playlist.IsRandom', TEXT2),
                                                   ('icon_shuffle.png', 'Playlist.IsRandom', ACCENT2)]),
        (ids.NP_PREV, 'PlayerControl(Previous)', [('icon_prev.png', None, TEXT)]),
        (ids.NP_PLAY, 'PlayerControl(Play)', [('icon_pause.png', '!Player.Paused', TEXT),
                                              ('icon_play.png', 'Player.Paused', TEXT)]),
        (ids.NP_NEXT, 'PlayerControl(Next)', [('icon_next.png', None, TEXT)]),
        (ids.NP_REPEAT, 'PlayerControl(Repeat)', [
            ('icon_repeat.png', '!Playlist.IsRepeat + !Playlist.IsRepeatOne', TEXT2),
            ('icon_repeat.png', 'Playlist.IsRepeat', ACCENT2),
            ('icon_repeat_one.png', 'Playlist.IsRepeatOne', ACCENT2)]),
        (ids.NP_FAVOURITE, None, [('icon_favourite_outline.png', 'String.IsEmpty(Window.Property(starred))', TEXT2),
                                  ('icon_favourite.png', '!String.IsEmpty(Window.Property(starred))', ACCENT)]),
        (ids.NP_MORE, None, [('icon_more.png', None, TEXT2)]),
    ]
    step = 90
    for index, (control_id, action, icons) in enumerate(layout):
        x = left - 10 + index * step
        size = 84 if control_id == ids.NP_PLAY else 72
        y = 960 - (size - 72) // 2
        previous = layout[index - 1][0] if index else None
        following = layout[index + 1][0] if index + 1 < len(layout) else to_tab
        if control_id == ids.NP_PLAY:
            buttons.append(image(x, y, size, size, 'btn_accent.png'))
        else:
            buttons.append(image(x, y, size, size, 'circle.png', '40FFFFFF', visible=f'Control.HasFocus({control_id})'))
        buttons.append(
            f'<control type="button" id="{control_id}"><left>{x}</left><top>{y}</top>'
            f'<width>{size}</width><height>{size}</height>'
            '<texturefocus></texturefocus><texturenofocus></texturenofocus><label></label>'
            + (f'<onclick>{action}</onclick>' if action else '')
            + nav(onup=ids.NP_SLIDER, onleft=previous, onright=following) + '</control>')
        if control_id == ids.NP_PLAY:
            buttons.append(image(x, y, size, size, 'ring_focus.png', TEXT, visible=f'Control.HasFocus({control_id})'))
        for texture, visible, color in icons:
            icon_size = 44 if control_id == ids.NP_PLAY else 38
            buttons.append(image(x + (size - icon_size) // 2, y + (size - icon_size) // 2, icon_size, icon_size,
                                 texture, color, visible=visible))

    panel_x, panel_w = 880, 920

    def tab(control_id, key, x, active):
        return (f'<control type="button" id="{control_id}"><left>{x}</left><top>96</top><width>260</width>'
                '<height>64</height>'
                f'<texturefocus border="32,0,32,0" colordiffuse="{TEXT}">pill.png</texturefocus>'
                '<texturenofocus></texturenofocus>'
                f'<label>{S(key)}</label><font>{F_LARGE}</font><align>center</align><aligny>center</aligny>'
                f'<textcolor>{TEXT3}</textcolor><focusedcolor>{DARK}</focusedcolor>'
                + nav(ondown=to_panel, onleft=ids.NP_PLAY if control_id == ids.NP_TAB_LYRICS else ids.NP_TAB_LYRICS,
                      onright=ids.NP_TAB_QUEUE if control_id == ids.NP_TAB_LYRICS else None)
                + '</control>'
                + label(x, 96, 260, 64, S(key), F_LARGE, TEXT, 'center',
                        visible=f'{active} + !Control.HasFocus({control_id})')
                + image(x + 100, 162, 60, 4, 'white.png', ACCENT2, visible=active))

    tabs = (
        label(panel_x, 50, 600, 36, S('np_title'), F_SMALL, ACCENT2)
        + tab(ids.NP_TAB_LYRICS, 'np_lyrics', panel_x, panel_lyrics)
        + tab(ids.NP_TAB_QUEUE, 'np_queue', panel_x + 280, panel_queue)
        + label(panel_x + panel_w - 400, 96, 400, 64, prop('queue.info'), F_SMALL, TEXT3, 'right',
                visible=panel_queue)
    )

    synced = lyrics_state('synced')
    short_line = 'String.IsEmpty(ListItem.Property(long))'
    # Noto Sans lines are 45 px (font32) and 63 px (font45_title) high: a row holds three
    # lines of F_LYRIC or two of F_LYRIC_NOW. Shorter rows cut wrapped lines off with "...".
    lyric_h = 136
    lyrics = (
        f'<control type="fixedlist" id="{ids.NP_LYRICS}"><left>{panel_x}</left><top>200</top>'
        f'<width>{panel_w}</width><height>{lyric_h * 6}</height><orientation>vertical</orientation>'
        '<focusposition>2</focusposition><movement>2</movement>'
        '<scrolltime tween="cubic" easing="out">450</scrolltime>'
        + nav(onup=to_tab, onleft=ids.NP_PLAY)
        + _visible(f'{panel_lyrics} + {has_lyrics}')
        + f'<itemlayout width="{panel_w}" height="{lyric_h}">'
        + label(0, 0, panel_w, lyric_h, '$INFO[ListItem.Label]', F_LYRIC, TEXT3, visible=synced, wrap=True)
        + label(0, 0, panel_w, lyric_h, '$INFO[ListItem.Label]', F_LYRIC, TEXT2, visible=f'!{synced}', wrap=True)
        + f'</itemlayout><focusedlayout width="{panel_w}" height="{lyric_h}">'
        + image(-20, 4, panel_w + 20, lyric_h - 8, 'round_12.png', FOCUS_ROW, border=12,
                visible=f'Control.HasFocus({ids.NP_LYRICS})')
        + label(0, 0, panel_w, lyric_h, '$INFO[ListItem.Label]', F_LYRIC_NOW, TEXT,
                visible=f'{synced} + {short_line}', wrap=True)
        + label(0, 0, panel_w, lyric_h, '$INFO[ListItem.Label]', F_LYRIC_NOW_LONG, TEXT,
                visible=f'{synced} + !{short_line}', wrap=True)
        + label(0, 0, panel_w, lyric_h, '$INFO[ListItem.Label]', F_LYRIC, TEXT2, visible=f'!{synced}', wrap=True)
        + '</focusedlayout></control>'
        + label(panel_x, 420, panel_w, 60, S('np_loading'), F_ITEM, TEXT3,
                visible=f'{panel_lyrics} + {lyrics_state("loading")}')
        + image(panel_x, 360, 56, 56, 'icon_lyrics.png', TEXT3,
                visible=f'{panel_lyrics} + {lyrics_state("none")}')
        + label(panel_x, 430, panel_w, 60, S('np_no_lyrics'), F_ITEM, TEXT2,
                visible=f'{panel_lyrics} + {lyrics_state("none")}')
    )

    current = 'String.IsEqual(ListItem.Property(current),1)'

    def queue_row(focused):
        return (
            (image(0, 4, panel_w, ROW - 8, 'round_12.png', FOCUS_ROW, border=12,
                   visible=f'Control.HasFocus({ids.NP_QUEUE})') if focused else '')
            + image(14, 10, ROW - 20, ROW - 20, '$INFO[ListItem.Art(thumb)]', diffuse='mask_round.png',
                    fallback='placeholder_album.png', aspect='scale', background=True)
            + image(14, 10, ROW - 20, ROW - 20, 'white.png', 'B30B0C14', diffuse='mask_round.png', visible=current)
            + image(14 + 12, 22, 36, 36, 'icon_equalizer.png', ACCENT2, visible=current)
            + label(ROW + 8, 10, panel_w - ROW - 140, 34, '$INFO[ListItem.Label]', F_ITEM, TEXT,
                    visible=f'!{current}', scroll=focused)
            + label(ROW + 8, 10, panel_w - ROW - 140, 34, '$INFO[ListItem.Label]', F_ITEM, ACCENT2,
                    visible=current, scroll=focused)
            + label(ROW + 8, 44, panel_w - ROW - 140, 28, '$INFO[ListItem.Label2]', F_SMALL, TEXT2)
            + label(panel_w - 120, 0, 100, ROW, '$INFO[ListItem.Property(duration)]', F_BODY, TEXT2, 'right')
        )

    queue = (
        f'<control type="list" id="{ids.NP_QUEUE}"><left>{panel_x}</left><top>200</top>'
        f'<width>{panel_w}</width><height>{ROW * 10}</height><orientation>vertical</orientation>'
        '<scrolltime tween="cubic" easing="out">250</scrolltime>'
        + nav(onup=to_tab, onleft=ids.NP_PLAY) + _visible(panel_queue)
        + f'<itemlayout width="{panel_w}" height="{ROW}">{queue_row(False)}</itemlayout>'
        + f'<focusedlayout width="{panel_w}" height="{ROW}">{queue_row(True)}</focusedlayout></control>'
    )

    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<!-- SPDX-License-Identifier: GPL-3.0-or-later. Generated by tools/make_skin.py - edit the generator, not this file. -->\n'
            f'<window><defaultcontrol always="true">{ids.NP_PLAY}</defaultcontrol>'
            '<animation effect="fade" time="250">WindowOpen</animation>'
            '<animation effect="fade" time="200">WindowClose</animation><controls>'
            + background_xml + artwork + meta + progress + ''.join(buttons) + tabs + lyrics + queue
            + '</controls></window>\n')


def pretty(source):
    return minidom.parseString(source.encode('utf-8')).toprettyxml(indent='  ', encoding='UTF-8') \
        .decode('utf-8').replace('<?xml version="1.0" encoding="UTF-8"?>',
                                 '<?xml version="1.0" encoding="UTF-8"?>\n'
                                 '<!-- SPDX-License-Identifier: GPL-3.0-or-later. Generated by tools/make_skin.py - edit the generator, not this file. -->', 1)


def main():
    os.makedirs(SKIN, exist_ok=True)
    for name, builder in (('script-auradeck-main.xml', main_window),
                          ('script-auradeck-nowplaying.xml', now_playing)):
        target = os.path.join(SKIN, name)
        text = pretty(builder())
        text = '\n'.join(line for line in text.splitlines() if line.strip())
        with open(target, 'w', encoding='utf-8') as handle:
            handle.write(text + '\n')
        print('written', target)


if __name__ == '__main__':
    main()
