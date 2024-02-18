Migrate
=======

.. _preflight:

Preflight Scans
---------------

1. To effectively migrate content the sphinx-build rst docs are scanned to collect information about the anchors, headings and downloads.

   .. code-block:: bash

      mkdocs_translate scan

2. Optional: You can run these scans independently:

   .. code-block:: bash

      mkdocs_translate scan downloads.

3. Optional: To troubleshoot an individual file, the resulting `index` can be sent to standard out:

   .. code-block:: bash

      mkdocs_translate scan download --test source/setup/index.rst

4. The following is produced during preflight scans:

   .. code-block:: text

      docs/setup/download/download.txt
      build/anchors.txt

   .. build/nav.yaml

.. _migrate:

Content Migration
-----------------

Format conversion from :command:`sphinx-build` reStructuredText files to :command:`mkdocs` Markdown content.

1. Copy everything over (so all the images and so on are present)

   .. code-block:: bash

      cd geoserver/doc/en/user
      copy -r source doc

2. Clean sphinx-build `conf.py` and ``rst`` files from `docs/` folder.

   .. code-block:: bash

      find doc -type f -regex ".*\.rst" -delete
      rm doc/conf.py

5. To bulk convert all content from :file:`rst` to :file:`md`:

   .. code-block:: bash

      mkdocs_translate migrate source/**/*.rst

6. Review this content you may find individual files to fix.

   Some formatting is easier to fix in the :file:`rst` files before conversion:

   * Indention of nested lists in :file:`rst` content is often incorrect, resulting in restarted numbering or block quotes.

   * Random ``{.title-ref}`` snippets is a general indication to simplify the rst and re-translate.

   * Anchors or headings with trailing whitespace throwing off the heading scan, resulting in broken references

7. Convert a single file:

   .. code-block:: bash

      mkdocs_translate rst source/introduction/license.rst

7. Bulk convert files in a folder:

   .. code-block:: bash

      mkdocs_translate rst source/introduction/**/*.rst

8. To generate out navigation tree:

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
