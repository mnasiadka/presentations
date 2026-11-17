# Build the reveal.js deck and export it to PDF with the local Chrome.
#
#   make html        -> _build/revealjs/index.html (open in a browser, "s" = speaker view)
#   make serve       -> build and serve on http://localhost:8000 for presenting
#   make pdf         -> kolla-2026.2.pdf        (one page per slide)
#   make pdf-steps   -> kolla-2026.2-steps.pdf  (one page per click)

SPHINXBUILD ?= $(HOME)/venv/bin/sphinx-build
BUILD := _build/revealjs
PRINT := node ../tools/revealjs_pdf.mjs $(BUILD)/index.html

.PHONY: html serve pdf pdf-steps all

html:
	$(SPHINXBUILD) -b revealjs -W . $(BUILD)

# Present from http://localhost:8000 (speaker view works reliably over http)
serve: html
	cd $(BUILD) && python3 -m http.server 8000 --bind 127.0.0.1

pdf: html
	$(PRINT) kolla-2026.2.pdf

pdf-steps: html
	$(PRINT) kolla-2026.2-steps.pdf --steps

all: pdf pdf-steps
