# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'MkDocs Translate'
copyright = '2024, Jody Garnett'
author = 'Jody Garnett'
version = "0.9"
release = "0.9.5"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['sphinx.ext.extlinks']

templates_path = ['_templates']
exclude_patterns = []

extlinks = {
    'github': ('https://github.com/jodygarnett/translate/blob/main/%s', '%s'),
    'release': ('https://github.com/jodygarnett/translate/releases/tag/%s', 'Release %s'),
    'squidfunk' : ('https://squidfunk.github.io/mkdocs-material/%s','%s')
}

smartquotes = False

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']


