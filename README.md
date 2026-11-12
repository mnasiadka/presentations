# Presentations

Conference talks written in reStructuredText and built into
[reveal.js](https://revealjs.com) slides with
[sphinx-revealjs](https://sphinx-revealjs.readthedocs.io). Everything a
deck needs (reveal.js, fonts, theme assets) is bundled, so built decks work
offline.

| Talk | Event |
|---|---|
| [Magnum After Heat](OpenInfra_Day_US_2026/) | OpenInfra Day US 2026 |

## Layout

```
<Event_Year>/       one directory per talk: conf.py, index.rst, Makefile
themes/openinfra/   OpenInfra Foundation speaker template (CSS, backgrounds, fonts)
tools/              revealjs_pdf.mjs: PDF export via the local Chrome
```

## Setup

```console
$ python3 -m venv ~/venv
$ ~/venv/bin/pip install -r requirements.txt
```

PDF export also needs Node.js (18+) and Google Chrome; set `CHROME` if
Chrome is not in `/Applications`.

## Working on a talk

```console
$ cd OpenInfra_Day_US_2026
$ make html        # build into _build/revealjs/
$ make serve       # build and serve on http://localhost:8000
$ make pdf         # one page per slide
$ make pdf-steps   # one page per click
```

Builds run with `-W`, so Sphinx warnings fail the build. PDFs and `_build/`
are not committed.

## Presenting

1. `make serve`, then open the slides in a chrome-less window:
   `open -na "Google Chrome" --args --new-window --app=http://localhost:8000`
2. Move that window to the projector and press `f` for full screen.
3. Press `s` for the speaker view (notes, next slide, timer) and keep it on
   the laptop screen; drive the talk from there.

Other keys: `b` blanks the screen, `o` shows the overview, `?` lists all
shortcuts.

## Starting a new talk

Copy `conf.py` and `Makefile` from an existing talk into a new
`<Event_Year>/` directory and write `index.rst`:

- Slides are `---` (level 2) sections; the level 1 title is the title slide.
- `.. revealjs-notes::` for speaker notes, `.. revealjs-fragments::` or a
  `fragment` class for click-by-click reveals.
- With the `openinfra` theme: `.. container:: section-label` for the
  `>>` label, `.. container:: dark` plus a `revealjs-section` with
  `:data-background-image: ../themes/openinfra/bg-dark.png` for black slides,
  and the `cards`, `steps`, `columns`, `callout` and `chips` containers for
  layout.

The theme's Roboto fonts are under the SIL Open Font License
(`themes/openinfra/Roboto-OFL.txt`).
