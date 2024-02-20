---
# YAML header
render_macros: false
---

# Getting started

## Installation {: #install }

A translate script is provided to facilitate working with pandoc and deepl translation services.

1.  To install development version use:

    ``` bash
    pip install git+https://github.com/jodygarnett/translate.git
    ```

2.  Install script requirements, and check it runs:

    ``` bash
    mkdocs_translate --help
    ```

3.  This script requires ***pandoc*** be installed:

    Ubuntu:

    ``` bash
    apt-get install pandoc
    ```

    macOS:

    ``` bash
    brew install pandoc
    ```

    !!! abstract "Reference"

        -   <https://pandoc.org/installing.html>

## Project setup {: #setup }

1.  A working [example](https://github.com/jodygarnett/translate/blob/main/example) is provided to be adapted for your project.

2.  Create [requirements.txt](../../requirements.txt) with mkdocs plugins required.

    ~~~text
    {% 
      include "../../requirements.txt"
    %}
    ~~~

3.  Create [mkdocs.yml](../../mkdocs.yml), the navigation tree is initially empty.

    ~~~yaml
    {% 
      include "../../mkdocs.yml"
       end="- setup/index.md"
    %}
    ~~~

4.  Create **`build/`** folder for temporary files during migration.

    ``` bash
    mkdir build
    ```

    !!! note

        If converting a ***maven*** project use of the existing **`target/`** folder can be configured below.

5.  Define [.gitingore](../../.gitignore) to avoid adding generated artifacts to version control.

    Create [.gitignore](../../.gitignore).

    ~~~text
    {% 
      include "../../.gitignore"
    %}
    ~~~

6.  The resulting directory structure is:

        docs/
        source/
        .gitignore
        download.py
        mkdocs.yml
        requirements.txt

## Download Hook {: #download_hook }

Optional: If your content uses `download`directive to include external content, there is a `mkdocs`hook for processing of `download.txt`files.

1.  Create [download.py](../../download.py).

    ~~~python
    {% 
      include "../../download.py"
    %}
    ~~~

2.  Register hook with `mkdocs.yml`

    ``` yaml
    # Customizations
    hooks:
    - download.py
    ```

    !!! note

        See writing guide [Download of external file](../guide/markdown.md#download_external) for example on how to use this hook.

3.  The resulting directory structure is:

        docs/
        source/
        download.py
        mkdocs.yml
        requirements.txt

## Configuration {: #config }

For simple python ***sphinx-build*** setup and directory structure no configuration is required.

-   To provide configuration for your project add a **`translate.yml`** to the project directory.

-   To override configuration on command line add `-config <file.yml>`before the command:

    ``` bash
    mkdocs_translate --config translate.yml migrate source/index.rst
    ```

To provide configuration for your project:

1.  Create a [translate.yml](../../translate.yml) to configure script for your project.

    ~~~yaml
    {% 
      include "../../translate.yml"
    %}
    ~~~

    !!! note

        The example above is for the example project, with `project` and `author` substitutions. This project also has `extlinks` defined that need to be known upfront during migration.

2.  Optional: Maven project [translate.yml](./files/translate.yml) configuration recommendations.

    ~~~yaml
    {% 
      include "./files/translate.yml"
    %}
    ~~~

3.  The resulting directory structure is:

        docs/
        source/
        .gitignore
        translate.yml
        mkdocs.yml
        requirements.txt

The configuration settings are:

-   `project_folder`: `.`

    Default assumes you are running from the current directory.

-   `docs_folder` `docs`

    mkdocs convention.

-   `build_folder` `build`

    The use of `build` follows sphinx-build and mkdocs convention, maven projects may wish to use `target`.

-   `rst_folder` `source`

-   `anchor_file` `anchors.txt`

-   `convert_folder` `migrate`

    Combined with `build_folder` for rst conversion temporary files (example: `build/migrate`. Temporary files are required for use by pandoc.

-   `upload_folder` `upload`

    Combined with `build_folder` to stage html files for internationalization (example: `build/upload`)

Internationalization configuration options:

-   `deepl_base_url`: `https://api-free.deepl.com`

    Customize if you have a subscription to deepl.

-   `download_folder` `download`

    Combined with `build_folder` to retrieve internationalization results (example: `build/download`) Temporary files are required for use by pandoc.

-   `substitutions` dictionary of `|substitutions|`to use when converting config.py rst_epilog common substitutions.

    ``` yaml
    project: GeoServer
    author: Open Source Geospatial Foundation
    copyright: 2023, Open Source Geospatial Foundation
    project_copyright: 2023, Open Source Geospatial Foundation
    ```

-   The built-in substitutions for `{{ version }}`and `{{ release }}`are changed to `{{ version }}` and `{{ release }}` variables for use with `mkdocs-macros-plugin`variable substitution:

    Use **`mkdocs.yml`** to define these variable substitutions:

    ``` yaml
    extra:
      homepage: https://geoserver.org/
      version: '2.24'
      release: '2.24.2'
    ```

-   `extlinks` dictionary of config.py extlinks substitutions taking the form:

    ``` 
    extlinks:
      wiki: https://github.com/geoserver/geoserver/wiki/%s
      user: https://docs.geoserver.org/{{ branch }}/en/user/%s
      geos: https://osgeo-org.atlassian.net/browse/GEOS-%s|GEOS-%s
      download_release: https://sourceforge.net/projects/geoserver/files/GeoServer/{{ release }}/geoserver-{{ release }}-%s.zip|geoserver-{{ release }}-%s.zip
    ```

    !!! note

        Use of `mkdocs-macros-plugin`for variable substitution of `release`above.
    
        Use of `|GEOS-%s` to override default link text `%s`.

    This handles the sphinx-build **`config.py`** extlinks during migration:

    ``` python
    extlinks = {
       'wiki': ('https://github.com/geoserver/geoserver/wiki/%s', '%s'),
       'user': ('https://docs.geoserver.org/'+branch+'/en/user/%s', '%s'),
       'geos': ('https://osgeo-org.atlassian.net/browse/GEOS-%s','GEOS-%s'),
       'download_release': ('https://sourceforge.net/projects/geoserver/files/GeoServer/' + release + '/geoserver-' + release + '-%s.zip', 'geoserver-' + release + '-%s.zip )
    }
    ```

-   'macro_ignore': Use of `mkdocs-macros-plugin`can conflict with code examples.

    This script adds the YAML header to enable macros to better support the use `{{ version }}`and `{{ release }}` If you find this accidentially is triggered by code examples you can add an ignore.
