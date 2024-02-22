Language Internationalization
=============================

To help manage a multi-language build is it kind to provide human translators with an example document to start from.

Setup
-----

The `mkdocs-static-i18n <https://ultrabug.github.io/mkdocs-static-i18n/>` plugin is setup based on suffix, with **`index.md`** is the default English, and **``index.fr.md``** used for French::

    | index.md
    | index.fr.md
    + img/
      | figure.png
      + figure.fr.png

The configuration of ``mkdocs-static-i18n`` is represented in :file:`mkdocs.yml` using:

.. code-block:: yaml

    plugins:
      - i18n:
          docs_structure: suffix
          reconfigure_material: true
          languages:
            - locale: en
              default: true
              name: English
            - locale: fr
              name: Français
              site_name: 'Aide en ligne'
              nav_translations:
                Home: Accueil
                Search: Recherche

.. _translate:

Language Translation
--------------------

Translation uses :command:`pandoc` to convert to `html`, and then using `Deepl REST API <https://deepl.com>`__.

1. Provide environmental variable with Deepl authentication key:

   .. code-block:: bash

      export DEEPL_AUTH="xxxxxxxx-xxx-...-xxxxx:fx"

2. Translate a document to french using pandoc and deepl:

   .. code-block:: bash

      mkdocs_translate french docs/help/index.md

3. To translate several documents in a folder:

   .. code-block:: bash

      mkdocs_translate french docs/overview/*.md

4. See ``mkdocs_translate french --help`` for more options.

Limitations
^^^^^^^^^^^

Keep in mind the following limitations:

* Deepl charges by the character so bulk translation not advisable.
* You are welcome to use google translate, ChatGPT, or Deepl directly - keeping in mind markdown formatting may be lost.
* Please see the :ref:`writing guide <markdown>` for what :command:`mkdocs` functionality is supported.

Specific ***pandoc*** extensions are used to match the capabilities of ***mkdocs***:

===================== ========================
markdown extension    pandoc extension
===================== ========================
tables                pipe_tables
pymdownx.keys
pymdownx.superfences  backtick_code_blocks
admonition            fenced_divs
===================== ========================

The differences differences in markdown requires pre/post processing of markdown and html files.
These steps are automated in the ***mkddoc_translate***, supporting additional ***mkdocs*** features
requires updating this script.
