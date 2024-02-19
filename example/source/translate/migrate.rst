Migrate
=======

.. _preflight:

Preflight
---------

1. Use init to create :file:`docs` directory and copy over non :file:`rst` files (such as images and sample data).

   .. code-block:: bash

      mkdocs_translate init

2. To effectively migrate content the sphinx-build rst docs are scanned to collect information about the anchors, headings and downloads.

   .. code-block:: bash

      mkdocs_translate scan

3. Optional: You can run these scans independently:

   .. code-block:: bash

      mkdocs_translate scan downloads.

4. Optional: To troubleshoot an individual file, the resulting `index` can be sent to standard out:

   .. code-block:: bash

      mkdocs_translate scan download --test source/setup/index.rst

5. The following is produced during preflight scans:

   .. code-block:: text

      docs/setup/download/download.txt
      build/anchors.txt

   .. build/nav.yaml

.. _migrate:

Content Migration
-----------------

Format conversion from :command:`sphinx-build` reStructuredText files to :command:`mkdocs` Markdown content.

1. To bulk convert all content from :file:`rst` to :file:`md`:

   .. code-block:: bash

      mkdocs_translate migrate

2. Review this content you may find individual files to fix.

   Some formatting is easier to fix in the :file:`rst` files before conversion:

   * Indention of nested lists in :file:`rst` content is often incorrect, resulting in restarted numbering or block quotes.

   * Random ``{.title-ref}`` snippets is a general indication to simplify the rst and re-translate.

   * Anchors or headings with trailing whitespace throwing off the heading scan, resulting in broken references

3. Convert a single file:

   .. code-block:: bash

      mkdocs_translate migrate source/introduction/license.rst

4. Bulk convert files in a folder:

   .. code-block:: bash

      mkdocs_translate migrate source/introduction/**/*.rst

5. To generate out navigation tree:

   .. code-block:: bash

      mkdocs_translate scan toc

   The output is printed to standard out and may be appended to :file:`mkdocs.yml` file.

Known limitations
-----------------

Some things are not supported by :command:`pandoc`, which will produce ``WARNING:`` messages:

* Substitutions used for inline images

* Underlines: replace with bold or italic

  ::

    WARNING: broken reference 'getting_involved' link:getting_involved-broken.rst
