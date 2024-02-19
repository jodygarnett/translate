Getting started
===============

.. _install:

Installation
------------

A translate script is provided to facilitate working with pandoc and deepl translation services.

1. To install development version use:

   .. code-block:: bash

      pip install git+https://github.com/jodygarnett/translate.git

2. Install script requirements, and check it runs:

   .. code-block:: bash

      mkdocs_translate --help

3. This script requires :command:`pandoc` be installed:

   Ubuntu:

   .. code-block:: bash

      apt-get install pandoc

   macOS:

   .. code-block:: bash

      brew install pandoc

   .. admonition:: Reference

      * https://pandoc.org/installing.html

.. _setup:

Project setup
-------------

1. A working :github:`example <example>` is provided to be adapted for your project.

2. Create :download:`requirements.txt <../../requirements.txt>` with mkdocs plugins required.

   .. literalinclude:: ../../requirements.txt
      :language: text

3. Create :download:`mkdocs.yml <../../mkdocs.yml>`, the navigation tree is initially empty.

   .. literalinclude:: ../../mkdocs.yml
      :language: yaml

4. Create :file:`docs/` folder for markdown content.

   .. code-block:: bash

      mkdir docs

5. Create :file:`build/` folder for temporary files during migration.

   .. code-block:: bash

      mkdir build

   .. note:: If converting a :command:`maven` project use of the existing :file:`target/` folder can be configured below.

5. Optional: Create a :download:`translate.yml <../../translate.yml>` to :ref:`configure <config>` script for your project.

   .. literalinclude:: ../../translate.yml
      :language: yaml

6. Optional: If your content uses `download` directive to include external content, there is a `mkdocs` hook for processing of `download.txt` files.

   Create :download:`download.py <../../download.py>`.

   .. literalinclude:: ../../download.py
      :language: python

   Register hook with `mkdocs.yml`:

   .. code-block:: yaml

      # Customizations
      hooks:
      - download.py

   .. note:: See writing guide :ref:`download_external` for example on how to use this hook.

7. Define :download:`.gitingore <../../.gitignore>` to avoid adding generated artifacts to version control.

   Create :download:`.gitignore <../../.gitignore>`.

   .. literalinclude:: ../../.gitignore
      :language: text

8. The resulting directory structure is:

   ::

       docs/
       source/
       .gitignore
       download.py
       mkdocs.yml
       requirements.txt
       translate.yaml

.. _config:

Configuration
-------------

For simple python :command:`sphinx-build` setup no configuration is required.

* To provide configuration for your project add a :file:`translate.yml` to the project directory.

* To override configuration on command line add `-config <file.yml>` before the command:

  .. code-block:: bash

     mkdocs_translate --config translate.yml migrate source/index.rst

The file `mkdocs_translate/config.yml` file contains some settings (defaults are shown below):

* `deepl_base_url`: "https://api-free.deepl.com"

  Customize if you have a subscription to deepl.

* `project_folder`: "."

  Default assumes you are running from the current directory.

* `rst_folder`: "source"

* `docs_folder`: "docs"

* `build_folder`: "build"

  The use of "target" follows maven convention, maven projects may wish to use `target`.

* `docs_folder`: "docs"

  mkdocs convention.

* `anchor_file`: 'anchors.txt'

* `upload_folder`: "upload"

  Combined with ``build_folder`` to stage html files for translation (example:  `build/upload`)

* `convert_folder`: "migrate"

  Combined with ``build_folder`` for rst conversion temporary files (example:  `build/migrate`).
  Temporary files are required for use by pandoc.

* `download_folder`: "download"

  Combined with ``build_folder`` to retrieve translation results (example:  `build/download`)
  Temporary files are required for use by pandoc.

* `substitutions`: dictionary of `|substitutions|` to use when converting config.py rst_epilog common substitutions.

  .. code-block:: yaml

     project: GeoServer
     author: Open Source Geospatial Foundation
     copyright: 2023, Open Source Geospatial Foundation
     project_copyright: 2023, Open Source Geospatial Foundation

* The built-in substitutions for  `|version|` and `|release|` are changed to ``{{ version }}`` and ``{{ release }}``
  variables for use with `mkdocs-macros-plugin` variable substitution:

  Use :file:`mkdocs.yml` to define these variable substitutions:

  .. code-block:: yaml

     extra:
       homepage: https://geoserver.org/
       version: '2.24'
       release: '2.24.2'

* `extlinks`: dictionary of config.py extlinks substitutions taking the form:

  .. code-block::

     extlinks:
       wiki: https://github.com/geoserver/geoserver/wiki/%s
       user: https://docs.geoserver.org/{{ branch }}/en/user/%s
       geos: https://osgeo-org.atlassian.net/browse/GEOS-%s|GEOS-%s
       download_release: https://sourceforge.net/projects/geoserver/files/GeoServer/{{ release }}/geoserver-{{ release }}-%s.zip|geoserver-{{ release }}-%s.zip

  .. note::

     Use of `mkdocs-macros-plugin` for variable substitution of `release` above.

     Use of ``|GEOS-%s`` to override default link text ``%s``.

  This handles the sphinx-build :file:`config.py` extlinks during migration:

  .. code-block:: python

     extlinks = {
        'wiki': ('https://github.com/geoserver/geoserver/wiki/%s', '%s'),
        'user': ('https://docs.geoserver.org/'+branch+'/en/user/%s', '%s'),
        'geos': ('https://osgeo-org.atlassian.net/browse/GEOS-%s','GEOS-%s'),
        'download_release': ('https://sourceforge.net/projects/geoserver/files/GeoServer/' + release + '/geoserver-' + release + '-%s.zip', 'geoserver-' + release + '-%s.zip )
     }

