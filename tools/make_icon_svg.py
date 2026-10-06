"""Draw the site icon: "ABC" in the game's colours with Leo the lion peeking up from below.

Writes, from fonts/fredoka-latin.woff2 (the game's title font, bold) and icons/leo.svg (Leo's face):
  icons/icon.svg           the icon on a rounded sky tile (browser tab, app install)
  icons/icon-small.svg     just "ABC", bigger, for the 16 px tab icon (Leo would be a blur there)
  icons/icon-full.svg      the icon edge to edge (phones round the corners themselves)
  icons/icon-maskable.svg  smaller, inside the round safe zone (Android round icons)
Then tools/make_icons.js draws the PNG and .ico sizes from them.
Usage: pip install fonttools brotli; python3 tools/make_icon_svg.py
"""
import os, re
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.boundsPen import BoundsPen

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ICONS = os.path.join(ROOT, 'icons')
# letter: (colour, darker colour for its 3D side), as in the game
COLOURS = {'A': ('#6c4cf0', '#4f33c9'), 'B': ('#ff5fa2', '#d63f80'), 'C': ('#1f6fe0', '#1552b0')}
TILE = '<rect x="1" y="1" width="62" height="62" rx="14"'
FULL = '<rect width="64" height="64"'


def glyphs():
    """Each letter's outline, its outside edge and its holes, as SVG path data (y going down), and its width."""
    font = instancer.instantiateVariableFont(TTFont(os.path.join(ROOT, 'fonts', 'fredoka-latin.woff2')), {'wght': 700})
    gs, cmap = font.getGlyphSet(), font.getBestCmap()
    def path(ops):
        pen = SVGPathPen(gs)
        RecordingPen.replay(type('R', (), {'value': ops})(), TransformPen(pen, (1, 0, 0, -1, 0, 0)))
        return pen.getCommands()
    out = {}
    for ch in 'ABC':
        g = gs[cmap[ord(ch)]]
        rec = RecordingPen(); g.draw(rec)
        contours, cur = [], []
        for op in rec.value:
            cur.append(op)
            if op[0] in ('closePath', 'endPath'): contours.append(cur); cur = []
        def area(c):
            b = BoundsPen(gs); RecordingPen.replay(type('R', (), {'value': c})(), b)
            x0, y0, x1, y1 = b.bounds
            return (x1 - x0) * (y1 - y0)
        outer = max(contours, key=area)
        holes = [op for c in contours if c is not outer for op in c]
        out[ch] = (path(rec.value), path(outer), path(holes) if holes else '', g.width)
    return out, font['OS/2'].sCapHeight


GLYPHS, CAP = glyphs()


def letters(cx, base, h, gap, lift, outline=1.4, depth=2.2):
    """'ABC' centred on cx, sitting on base, cap height h: a white sticker edge and a 3D side (both around the outside), then the letter."""
    k = h / CAP
    widths = [GLYPHS[c][3] * k for c in 'ABC']
    x = cx - (sum(widths) + gap * 2) / 2
    edge, side, face, masks = [], [], [], []
    for c, w, up in zip('ABC', widths, lift):
        y = base - up
        at = lambda dy: f'transform="translate({x:.2f} {y + dy:.2f}) scale({k:.5f})"'
        fill, dark = COLOURS[c]
        edge.append(f'<use href="#{c}o" {at(depth / 2)} fill="none" stroke="#fff" stroke-width="{(2 * outline + depth) / k:.0f}" stroke-linejoin="round"/>')
        steps = round(depth / 0.4)
        copies = ''.join(f'<use href="#{c}o" {at(depth * (steps - i) / steps)} fill="{dark}"/>' for i in range(steps))
        if GLYPHS[c][2]:   # the side does not show through the letter's holes (B, A): they stay clear
            masks.append(f'<mask id="m{c}" maskUnits="userSpaceOnUse" x="-20" y="-20" width="104" height="104"><rect x="-20" y="-20" width="104" height="104" fill="#fff"/><use href="#{c}h" {at(0)} fill="#000"/></mask>')
            copies = f'<g mask="url(#m{c})">{copies}</g>'
        side.append(copies)
        face.append(f'<use href="#{c}" {at(0)} fill="{fill}"/>')
        x += w + gap
    return ''.join(masks + edge + side + face)


def leo(transform):
    body = open(os.path.join(ICONS, 'leo.svg'), encoding='utf-8').read()
    body = re.sub(r'<!--.*?-->|<svg[^>]*>|</svg>', '', body, flags=re.S)
    return f'<g transform="{transform}">' + re.sub(r'\n\s*', '', body) + '</g>'


def svg(bg, art, clip=''):
    defs = ('<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#aee3ff"/><stop offset="1" stop-color="#fff4d6"/></linearGradient>'
            + ''.join(f'<path id="{c}" d="{d}"/><path id="{c}o" d="{edge}"/>' + (f'<path id="{c}h" d="{holes}"/>' if holes else '') for c, (d, edge, holes, _) in GLYPHS.items())
            + (f'<clipPath id="tile">{clip}/></clipPath>' if clip else ''))
    return ('<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 64 64">\n'
            '<!-- Phonics Fun: "ABC" with Leo the lion (tools/make_icon_svg.py draws this) -->\n'
            f'<defs>{defs}</defs>\n{bg} fill="url(#sky)"/>\n{art}\n</svg>\n')


abc = letters(32, 28, 20, -1.4, [0, 2.5, 0])
leo_peeks = leo('translate(14.5 31) scale(.55)')
files = {
    'icon.svg': svg(TILE, f'<g clip-path="url(#tile)">{leo_peeks}</g>{abc}', TILE),
    'icon-small.svg': svg(TILE, letters(32, 44, 23.5, -3.2, [0, 3.5, 0])),
    'icon-full.svg': svg(FULL, f'<g clip-path="url(#tile)">{leo_peeks}</g>{abc}', FULL),
    'icon-maskable.svg': svg(FULL, f'<g transform="translate(6.4 6.4) scale(.8)">{leo_peeks}{abc}</g>'),
}
for name, text in files.items():
    with open(os.path.join(ICONS, name), 'w', encoding='utf-8') as f:
        f.write(text)
    print(f'icons/{name}: {len(text)} bytes')
