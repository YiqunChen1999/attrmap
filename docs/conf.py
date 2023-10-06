# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys
import sphinx_rtd_theme
CURR_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(CURR_DIR, '..'))
sys.path.append(os.path.join(CURR_DIR, '../attrmap'))
sys.path.append(CURR_DIR)


project = 'attrmap'
copyright = '2022, Yiqun Chen'
author = 'Yiqun Chen'
release = '0.0.7'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'recommonmark',
    # 'sphinx_markdown_tables',
    'sphinx.ext.autodoc',
    'sphinx_rtd_theme',
 ]
# source_suffix = '.md'
templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
html_static_path = ['_static']
