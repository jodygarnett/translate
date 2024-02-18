Development
===========

Local Development
-----------------

To build and test locally:

1. Clone:

   .. code-block:: bash

      git clone https://github.com/jodygarnett/translate.git translate

2. Install requirements:

   .. code-block:: bash

      cd translate
      pip3 install -r mkdocs_translate/requirements.txt

3. Install locally:

   .. code-block:: bash

      pip3 install -e .

Debugging
---------

1. Recommend troubleshooting a single file at a time:

   .. code-block:: bash

      mkdocs_translate migrate source/index.rst

2. Compare the temporary files staged for pandoc conversion:

   .. code-block:: bash

      bbedit source/index.rst docs/index.md build/migrate/index.tmp.html build/migrate/index.tmp.md

3. To turn on logging during migrating a file:

   .. code-block:: bash

      mkdocs_translate --log=DEBUG migrate source/index.rst

4. To troubleshoot indexing when scanning a single document:

   .. code-block:: bash

      mkdocs_translate --log=DEBUG scan index --TEST source/index.rst

   The index information is sent to standard out (rather than added to a :file:`anchor.txt` file.

4. To troubleshoot downloads when scanning a single document:

   .. code-block:: bash

      mkdocs_translate --log=DEBUG scan download --TEST source/index.rst

   The download information is sent to standard out (rather than a :file:`download.txt` file.

Pandoc
------

1. The pandoc plugin settings are in two constants:

   .. code-block:: python

        md_extensions_to =
            'markdown+definition_lists+fenced_divs+backtick_code_blocks+fenced_code_attributes-simple_tables+pipe_tables'
        md_extensions_from =
            'markdown+definition_lists+fenced_divs+backtick_code_blocks+fenced_code_attributes+pipe_tables'

2. The pandoc extensions are chosen to align with mkdocs use of markdown extensions, or with post-processing:

   ==================== ======================= ==================
   markdown extension   pandoc extension        post processing
   ==================== ======================= ==================
   tables               pipe_tables
   pymdownx.keys                                post processing
   pymdownx.superfences backtick_code_blocks    post processing
   admonition           fenced_divs             post processing
   ==================== ======================= ==================

3. Language translation depends on conversion to and from html. To troubleshoot just the markdown to html conversion:

   .. code-block:: bash

      mkdocs_translate internal_html docs/contributing/style-guide.md
      mkdocs_translate internal_markdown build/convert/contributing/style-guide.html

      diff docs/contributing/style-guide.md build/convert/contributing/style-guide.md

   Langauge conversion uses `text/html` to avoid internationalization of content distributing markdown formatting.