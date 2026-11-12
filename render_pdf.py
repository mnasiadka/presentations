"""Render a presentty deck to a PDF, one page per slide.

Usage: ~/venv/bin/python render_pdf.py <deck>.rst [out.pdf]
           [--size 80x25] [--light] [--progressive] [--font /path/to/mono.ttf]

By default each slide is one page with every progressive item revealed.
With --progressive, slides with progressive items get one page per step,
as presentty shows them when stepping through with the arrow keys.
"""

import argparse
import os

from PIL import Image, ImageDraw, ImageFont

from presentty import palette, rst, slide

FONTS = ['/System/Library/Fonts/Menlo.ttc',
         '/System/Library/Fonts/Monaco.ttf',
         '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf']


def rgb(spec, fallback):
    """Return (fg, bg) RGB tuples for an urwid AttrSpec."""
    vals = spec.get_rgb_values() if spec is not None else (None,) * 6
    fg = vals[:3] if None not in vals[:3] else fallback[0]
    bg = vals[3:] if None not in vals[3:] else fallback[1]
    return tuple(fg), tuple(bg)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('file')
    ap.add_argument('out', nargs='?')
    ap.add_argument('--size', default='80x25')
    ap.add_argument('--light', action='store_true')
    ap.add_argument('--progressive', action='store_true',
                    help='one page per progressive step')
    ap.add_argument('--font', default=next(
        (f for f in FONTS if os.path.exists(f)), None))
    ap.add_argument('--font-size', type=int, default=28)
    args = ap.parse_args()
    out = args.out or os.path.splitext(args.file)[0] + '.pdf'
    cols, rows = (int(x) for x in args.size.split('x'))

    plt = palette.LIGHT_PALETTE if args.light else palette.DARK_PALETTE
    hinter = slide.ScreenHinter()
    hinter.setScreen(type('S', (), {'get_cols_rows': lambda s: (cols, rows)})())
    program = rst.PresentationParser(plt, hinter).parse(
        open(args.file, encoding='utf-8').read(), args.file)

    font = ImageFont.truetype(args.font, args.font_size)
    cw = font.getlength('M')
    ascent, descent = font.getmetrics()
    ch = ascent + descent
    margin = int(cw * 2)
    default = rgb(plt['_default'], ((200, 200, 200), (0, 0, 0)))

    def draw_page(canvas):
        img = Image.new('RGB', (int(cols * cw) + 2 * margin,
                                rows * ch + 2 * margin), default[1])
        draw = ImageDraw.Draw(img)
        for y, line in enumerate(canvas.content()):
            x = 0
            for attr, _cs, text in line:
                text = text.decode('utf8')
                fg, bg = rgb(attr, default)
                px, py = margin + x * cw, margin + y * ch
                draw.rectangle([px, py, px + len(text) * cw, py + ch], fill=bg)
                # Place each character on the grid so box drawing lines up
                for i, c in enumerate(text):
                    if c != ' ':
                        draw.text((px + i * cw, py), c, font=font, fill=fg)
                x += len(text)
        return img

    pages = []
    for s in program:
        if args.progressive:
            states = range(len(s.progressives) + 1)
        else:
            states = [len(s.progressives)]  # show every progressive item
        for state in states:
            s.setProgressive(state)
            pages.append(draw_page(s.render((cols, rows))))

    pages[0].save(out, save_all=True, append_images=pages[1:], resolution=150)
    print('wrote %s (%d pages)' % (out, len(pages)))


if __name__ == '__main__':
    main()
