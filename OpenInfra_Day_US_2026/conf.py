# Sphinx configuration for the reveal.js version of the talk.
# Build with:  make html   (see Makefile for pdf targets)

project = "Magnum After Heat"
author = "Michal Nasiadka"
root_doc = "index"
exclude_patterns = ["_build"]

extensions = ["sphinx_revealjs"]

revealjs_style_theme = "white"
# Shared themes are copied to _static/<theme>/.
revealjs_static_path = ["../themes"]
revealjs_css_files = ["openinfra/openinfra.css"]

revealjs_script_conf = {
    # 16:9 canvas; reveal.js scales it to the screen.
    "width": 1280,
    "height": 720,
    "margin": 0.04,
    "center": False,
    "hash": True,
    "slideNumber": "c/t",
    "transition": "fade",
    "transitionSpeed": "fast",
    # PDF export: one page per slide unless overridden in the URL
    # (?print-pdf&pdfSeparateFragments=true gives one page per step).
    "pdfSeparateFragments": False,
}

revealjs_script_plugins = [
    # Speaker view with notes, next slide and timer: press "s".
    {"name": "RevealNotes", "src": "revealjs/plugin/notes/notes.js"},
    # sphinx-revealjs emits <pre><code class="lang"> for highlight.js;
    # token colours are in the theme CSS.
    {"name": "RevealHighlight", "src": "revealjs/plugin/highlight/highlight.js"},
]
