# Magnum After Heat: Pluggable Cluster API Drivers and the Road to Self-Managing Kubernetes

OpenInfra Day US 2026, 20 minutes. Uses the shared `openinfra` theme
(`../themes/openinfra/`).

```console
$ make html        # -> _build/revealjs/index.html
$ make serve       # build and serve on http://localhost:8000 for presenting
$ make pdf         # -> magnum-after-heat.pdf        (one page per slide)
$ make pdf-steps   # -> magnum-after-heat-steps.pdf  (one page per click)
```

Slides and speaker notes are in `index.rst`; diagrams are inline SVG in the
same file.

Sources: open reviews in
[openstack/magnum-specs](https://review.opendev.org/q/project:openstack/magnum-specs+is:open),
mainly change 997690 (k8s_kubeadm_v1 management cluster driver), plus
999596 (hosted control plane), 1010486 (add-ons), 960429 (upgrade API),
955549 (driver API validation) and 943358 (label normalisation).
