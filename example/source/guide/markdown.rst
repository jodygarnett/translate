.. _markdown:

Markdown
--------

These markdown conventions are carefully constructed for consistent representation of user interface elements, files, data and field input.

============================ ==========================
Markdown                     Directive
============================ ==========================
\*\*strong\*\*               gui label, menu selection
\`monospace\`                text input, item selection
\*emphasis\*                 figure (caption)
\*\*\*strong-emphasis\*\*\*  application, command
\*\*\`monospace-strong\`\*\* file
============================ ==========================

.. note::

   The above conventions are important for consistency and are required by the translation process.

   As an example we do not wish to translate keyboard input, so these are represented as monospace text input.

User interface components
^^^^^^^^^^^^^^^^^^^^^^^^^

Use `**strong**` to name user interface components for interaction (press for buttons, click for link).

Preview:

  Navigate to :menuselection:`Data --> Layers` page,
  and press :guilabel:`Add` to create a new layer.

Markdown uses  `**strong**`:

.. code-block:: markdown

   Navigate to **Data > Layers** page,
   and press **Add** to create a new layer.

Rich structured text uses `menuselection` and `guilabel` directives:

.. code-block:: reStructuredText

   Navigate to :menuselection:`Data --> Layers` page,
   and press :guilabel:`Add` to create a new layer.

Selected input
^^^^^^^^^^^^^^

Use \`item\` for user selected input, or item in a list or tree:

Preview:

  Select ``Basemap`` layer.

Markdown uses monospace:

.. code-block:: markdown

   Select `Basemap` layer.

Rich structured text uses monospace:

.. code-block:: reStructuredText

   Select ``Basemap`` layer.

Input text
^^^^^^^^^^

Use ``monospace`` for user supplied text input:

Preview:

  Use the :guilabel:`Search` field to enter: `Ocean*`

Markdown uses monospace:

.. code-block:: markdown

   Use the **Search** field enter: `Ocean*`

Rich structured text uses ``kbd`` directive:

.. code-block:: reStructuredText

   Use the :guilabel:`Search` field to enter: ``Ocean*``

Keypress
^^^^^^^^

Use ``key`` directive for keyboard keys.

Preview:

  Press :kbd:`Control-s` to search.

Markdown uses **mkdocs-material** :squidfunk:`keys <reference/formatting/#adding-keyboard-keys>` formatting:

.. code-block:: markdown

   Press ++control+s++ to search.

Rich structured text:

.. code-block:: reStructuredText

   Press :kbd:`Control-s` to search.

Form input
^^^^^^^^^^

Use definition list to document data entry. The field names use strong as they name a user interface element. Field values to input uses monspace as user input to type in.

Preview:

  #. To login as the GeoServer administrator using the default password:

     User:
        :kbd:`admin`

     Password:
         :kbd:`geoserver`

     Remember me
         Unchecked

     Press :guilabel:`Login`.

Markdown: definition lists

.. code-block:: markdown

   1.  To login as the GeoServer administrator using the default password:

       **User**

       :   `admin`


       **Password**

       :   `geoserver`


       **Remember me**

       :   Unchecked

       Press **Login**.

Rich structured text: list-table

.. code-block:: reStructuredText

   #. To login as the GeoServer administrator using the default password:

      .. list-table::
         :widths: 30 70
         :width: 100%
         :stub-columns: 1

         * - User:
           - :kbd:`admin`
         * - Password:
           - :kbd:`geoserver`
         * - Remember me
           - Unchecked

      Press :guilabel:`Login`.

Applications, commands and tools
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Use **bold** with *italics* for proper names of applications, commands, tools, and products.

Preview:

  Launch :command:`pgAdmin` and connect to the ``tutorial`` database.

Markdown:

.. code-block:: markdown

   Launch ***pgAdmin*** and connect to the `tutorial` database.

Rich structured text uses ``command`` directive:

.. code-block:: reStructuredText

   Launch :command:`pgAdmin` and connect to the ``tutorial`` database.

Files
^^^^^

Use **bold** with ``monospace`` for files and folders:

Preview

  See configuration file
  :file:`WEB-INF/config-security/config-security-ldap.xml`
  for details

Markdown:

.. code-block:: markdown

   See configuration file
   **`WEB-INF/config-security/config-security-ldap.xml`**
   for details

Rich structured text:


.. code-block:: reStructuredText

   See configuration
   file :file:`WEB-INF/config-security/config-security-ldap.xml`
   for details

Links and references
^^^^^^^^^^^^^^^^^^^^

Internal References
"""""""""""""""""""

Reference to other section of the document (some care is required to reference a specific heading):

  Authors have access to :ref:`translation <translate>` for initial draft.

Markdown use of relative links and anchor:

.. code-block:: markdown

   Authors have access to [translation](../translate/language#translate) for initial draft.

reStructuredText use of ``ref`` directive:

.. code-block:: reStructuredText

   Authors have access to :ref:`translation <translate>` for initial draft.

Download of sample file
"""""""""""""""""""""""

Sample file included in the documentation:

  Download schema :download:`example.txt <files/example.txt>`.

Markdown relative link, with text following **bold** with `monospace` file convention above:

.. code-block:: markdown

   Download text [**`example.txt`**](files/example.txt).

You may also experiment with mkdocs attr_list to supply a filename:

.. code-block:: markdown

   Download text [**`example.txt`**](files/example.txt) {:download="example.txt"} .

reStructured text uses ``downlaod`` directive:

.. code-block:: reStructuredText

   Download text :download:`example.txt <files/example.txt>`.

.. _download_external:

Download of external file
"""""""""""""""""""""""""

To include sample file from outside of the documentation tree:

  Open-source :download:`LICENSE.md </../../LICENSE.md>`

.. note::

   This functionality is not supported by Material for mkdocs (or any plugin I could find).
   It is accomplished using the :file:`download.py` hook described in :ref:`setup <download_hook>`.

To use :file:`download.py` hook, create a :file:`download` folder to hold staged files

Markdown refers to this folder using a relative link (like normal):

.. code-block:: markdown

   Open-source [**`LICENSE.md`**](download/LICENSE.md)

Create :file:`download/download.txt` with list of files to stage during :command:`mkdocs` build process:

.. literalinclude:: files/download.txt
   :language: text
   :caption: download.txt

reStructuredText uses ``download`` directive with relative path (you may starting leading :file:`/` to indicate the root of the documentation :file:`source` folder):

.. code-block:: reStructuredText

   Open-source :download:`LICENSE.md </../../LICENSE.md>`

Icons, Images and Figures
^^^^^^^^^^^^^^^^^^^^^^^^^

Icons
"""""

Material for mkDocs has extensive :squidfunk:`icon support <reference/icons-emojis/>`, for many user interface elements we can directly make use of the appropriate icon in Markdown:

.. code-block:: markdown

   1.  Press the *Validate :fontawesome-solid-check:* button at the top of the page.

Custom icons
""""""""""""

.. |osgeo_mark| image:: img/osgeo_mark.svg
   :width: 20
   :height: 20

Custom icons:

   |osgeo_mark| Empower everyone with open source geospatial

Material for MkDocs provides support for custom icons:

.. code-block:: markdown

   :osgeo-logo: Empower everyone with open source geospatial

Add images to :file:`overrides/.icons/` (yes it is a hidden folder)::

   overrides/
   - .icons/
     - osgeo/
       logo.svg

reStructuredText does not offer custom icons, the closest is the use of substitutions to "inline" and image.

.. literalinclude:: custom_icon_rst.txt
   :language: rst

.. warning::

   The :command:`mkdocs_translate` and :command:`pandoc` combo is unable to convert inline images at this time.

   ::

      [WARNING] Reference not found for 'Key "osgeo_mark"' at build/migrate/guide/markdown.tmp.prep.rst_chunk line 5 column 13


Figures
"""""""

Figures are used frequently to allow a caption to describe screen shots and diagrams.

   .. figure:: img/foss4g.svg
      :scale: 25%
      :alt: FOSS4G

      Free and Open Source Software for Geospatial

Markdown handles figures are handled by convention adding emphasized text after each image.

.. code-block:: markdown

   ![FOSS4G](img/foss4g.svg)
   *Free and Open Source Software for Geospatial*

.. note::

   The convention above depends on CSS rules in :file:`overrides/assets/stylesheets/extra.css`
   to provide a consistent presentation:

   .. literalinclude:: /../overrides/assets/stylesheets/extra.css
      :language: css

.. note::

   The official Material for MkDocs answer for :squidfunk:`images with captions <reference/images/#image-captions>` is to use ``md_in_html`` extension:

   .. code-block:: markdown

      <figure markdown="span">
        ![FOSS4G](img/foss4g.svg){ scale="25%" }
        <figcaption>Free and Open Source Software for Geospatial</figcaption>
      </figure>

reStructuredText has a ``figure`` directive:

.. code-block:: reStructuredText

   .. figure:: img/foss4g.svg
      :scale: 25%
      :alt: FOSS4G

      Free and Open Source Software for Geospatial

Images
""""""

Image content:

  .. image:: img/foss4g.svg
     :scale: 25%

Markdown provides inline image syntax.

.. code-block:: markdown

   ![](img/foss4g.svg)

Use of mkdocs att_list can be used to adjust scale:

.. code-block:: markdown

   ![](img/foss4g.svg){ scale="25%" }

reStructuredText has an ``image`` directive:

.. code-block:: reStructuredText

  .. image:: img/foss4g.svg
     :scale: 25%

Tables
^^^^^^

Material for MkDocs :squidfunk`data tables <reference/data-tables/>` use pipe-tables approach (supported by both :command:`mkdocs` and :command:`pandoc`):

Leading `|` tailing `|`:

.. code-block:: markdown

   | First Header | Second Header | Third Header |
   |--------------|---------------|--------------|
   | Content Cell | Content Cell  | Content Cell |
   | Content Cell | Content Cell  | Content Cell |

Column alignment using `:`

.. code-block:: markdown

   | First Header | Second Header | Third Header |
   |:-------------|:-------------:|-------------:|
   | Left         |    Center     |        Right |
   | Left         |    Center     |        Right |

Inline content
^^^^^^^^^^^^^^

Use of `mkdocs-include-plugin <https://github.com/mondeja/mkdocs-include-markdown-plugin>`__ provides ability to inline content.
Example project uses following :file:`mkdocs.yml` setup:

.. code-block:: yaml

   plugins:
     - include-markdown:
         preserve_includer_indent: true
         dedent: true
         comments: false

The official Material for mkdocs guidance is to use
:squidfunk:`snippets <setup/extensions/python-markdown-extensions/#snippets>` however this did not offer
the ability to include code examples and configuration from outside the document tree.

.. admonition:: Reference

   * `mkdocs-include-markdown-plugin <https://pypi.org/project/mkdocs-include-markdown-plugin/>`__
   * `mkdocs-exclude <https://pypi.org/project/mkdocs-exclude/>`__

include content
"""""""""""""""

Inlining a snippet from another file is helpful for material such as disclaimers or statements which are repeated in text.

  Empower everyone with open source geospatial

Here is a snippet to include markdown files inline, requires opening tag ``{%`` and closing tag ``%}``:

.. literalinclude:: include_md.txt
   :language: markdown

.. note:: Placeholders `{/` and `/}` used to indicate location of `{%` and `%}` in above code example.

Writers can use ``include-markdown`` with a glob pattern to inline many files, and an option to adjusting header level.
Together these two features can be used break up longer pages into more manageable size.

This takes the place of the sphinx-build ``include`` directive:

.. literalinclude:: include_rst.txt
   :language: rst

.. note::

   You may wish to use the :file:`txt` extension for
   included content. If you wish to use :file:`md` extension you can adjust :file:`mkdocs.yml` ``exclude`` or not
   ``not_in_nav`` to address warnings.

   .. code-block:: yaml

      plugins:
        - exclude:
            glob:
              - '**/files/*.md'

include config and code
"""""""""""""""""""""""

Including configuration and code examples:

   .. code-block:: xml

      <CharacterString>da165110-88fd-11da-a88f-000d939bc5d8</CharacterString>

Use `include` to include normal files, with optional use of start and end markers to capture a snippet, and dedent for appearance.

In this case we are including content into an xml code block to provide syntax highlighting, requires opening tag ``{%`` and closing tag ``%}``
within the code block:

.. literalinclude:: include_code_md.txt
   :language: markdown
   :dedent:

.. note:: Placeholders `{/` and `/}` used to indicate location of `{%` and `%}` in above code example.

This takes the place of the sphinx-build ``literal-include`` directive:

.. literalinclude:: include_code_rst.txt
   :language: rst
   :dedent:
