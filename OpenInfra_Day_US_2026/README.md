# Magnum After Heat: Pluggable Cluster API Drivers and the Road to Self-Managing Kubernetes

OpenInfra Day US 2026, 20 minutes.

`revealjs/` holds the talk as a Sphinx + sphinx-revealjs deck with
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
