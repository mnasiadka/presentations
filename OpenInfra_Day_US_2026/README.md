# Magnum After Heat: Pluggable Cluster API Drivers and the Road to Self-Managing Kubernetes

OpenInfra Day US 2026, 20 minutes.

Slides are written for [presentty](https://github.com/mnasiadka/presentty)
(Python 3 port on the `python3` branch).

```console
$ ~/venv/bin/pip install git+https://github.com/mnasiadka/presentty@python3
$ ~/venv/bin/presentty --warnings magnum-after-heat.rst   # validate
$ ~/venv/bin/presentty magnum-after-heat.rst              # present
$ ~/venv/bin/presentty-console magnum-after-heat.rst      # speaker notes + timer
```

Use a 256-colour terminal of at least 80x25. Arrow keys navigate, `q` quits.

presentty has no PDF export, so `../render_pdf.py` (shared by all decks)
renders each slide with presentty's own renderer (progressive items fully
revealed) into a PDF page:

```console
$ ~/venv/bin/python ../render_pdf.py magnum-after-heat.rst            # -> magnum-after-heat.pdf
$ ~/venv/bin/python ../render_pdf.py magnum-after-heat.rst --light    # light palette
$ ~/venv/bin/python ../render_pdf.py magnum-after-heat.rst --size 100x30
$ ~/venv/bin/python ../render_pdf.py magnum-after-heat.rst --light --progressive \
      magnum-after-heat-light-progressive.pdf   # one page per reveal step
```

## reveal.js version (graphics)

`revealjs/` holds the same talk as a Sphinx + sphinx-revealjs deck with
SVG diagrams and click-by-click reveals, styled after the OpenInfra
Foundation speaker template (brand colours, Roboto / Roboto Condensed,
four-colour strip and OpenInfra mark; assets in `_static/template/`).
Everything (reveal.js, fonts, plugins) is bundled locally, so it works
offline.

```console
$ ~/venv/bin/pip install sphinx sphinx-revealjs
$ cd revealjs
$ make html        # -> _build/revealjs/index.html
$ make pdf         # -> ../magnum-after-heat-revealjs.pdf        (one page per slide)
$ make pdf-steps   # -> ../magnum-after-heat-revealjs-steps.pdf  (one page per click)
```

Present by opening `_build/revealjs/index.html` in Chrome: `f` for full
screen, `s` for the speaker view (notes, next slide, timer), arrow keys or a
clicker to advance. PDF export uses `../../revealjs_pdf.mjs` (Node + the
installed Chrome, no npm packages).

Sources: open reviews in
[openstack/magnum-specs](https://review.opendev.org/q/project:openstack/magnum-specs+is:open),
mainly change 997690 (k8s_kubeadm_v1 management cluster driver), plus
999596 (hosted control plane), 1010486 (add-ons), 960429 (upgrade API),
955549 (driver API validation) and 943358 (label normalisation).
