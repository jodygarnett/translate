# MkDocs Translate

A translate script is provided to facilitate working with pandoc and deepl translation services.

The user manual is available: https://jodygarnett.github.io/translate/

The user manual is written in sphinx reStructuredText and translated to mkdocs as a regression test:

* https://github.com/jodygarnett/translate/tree/main/example 

## Quickstart

1. This script requires ***pandoc*** be installed:

   Ubuntu:
   ```bash
   apt-get install pandoc
   ```

   macOS:
   ``` bash
   brew install pandoc
   ```

   References:

   * https://pandoc.org/installing.html


2. A writable python environment is required.
   
   If you use homebrew (popular on macOS). This installs into user space so it is a witable environment.
   
   ```bash
   brew install python
   ```
   
   You may also use the system python provided by:
   
   * Linux distribution
   * Microsoft App Store
   * https://www.python.org/ (windows and macOS)
   
   The system python is not used directly, it includes `virtualenv` used to setup a writable Python enviornment:
   
   ```bash
   virtualenv venv
   source venv/bin/activate
   ```

3. Install mkdocs_translate into your writable Python environment.

   To install from pypi (not yet available):
   
   ```
   pip install mkdocs_translate
   ```
   
   To install development version use (to preview and provide feedback):

   ```
   pip install git+https://github.com/jodygarnett/translate.git
   ```
   
   
4. To check it is installed correctly:

   ```
   mkdocs_translate --help
   ```

5. The script is intended to run from the location of your mkdocs project (with `docs` and `mkdocs.yml` files):

   ```
   cd core-genetwork/docs/manual
   ```

6. The script makes use of existing ``build`` (or ``target``) folder for scratch files:

   ```
   mkdir build
   ```

7. Optional: Create a [translate.yml](translate.yml) filling in the conversion parameters for your project.

   This file is used to indicate the `build` or `target` directory to use for temporary files.
    
   Additional configuration options are required for advanced sphinx-build `config.py` options like substitutions and external links.

## Setting up mkdocs project

A working [example](example) is provided to be adapted for your project:

1. Create [requirements.txt](example/requirements.txt) with mkdocs plugins required.

2. Create [mkdocs.yml](example/mkdocs.yml). 

3. Optional: If your content uses `download` directive to include external content, there is a `mkdocs` hook for processing of `download.txt` files. 
   
   Create [download.py](example/download.py).

   Register hook with `mkdocs.yml`:
       
   ```yaml
   # Customizations
   hooks:
    - download.py
   ```

4. Use `.gitignore` to ignore the following:
   
    ```
    build
    target
    ```

5. The resulting directory structure is:
   
   ```
   doc/
   source/
   .gitignore 
   requirements.txt
   mkdocs.yml
   download.py
   ```

## Format conversion from sphinx-build rst files

GeoServer is used as an example here, which is a maven project with a convention of `target` for temporary files.

1. Copy everything over (so all the images and so on are present)
   
    ```
    cd geoserver/doc/en/user
    copy -r source doc
    ```
   
2. Clean sphinx-build `conf.py` and ``rst`` files from `docs/` folder.

    ```
    find doc -type f -regex ".*\.rst" -delete
    rm doc/conf.py
    ```

4.  To scan rst files before conversion:

    * `all`: (default)
    * `index`: scan anchors and headings into `target/convert/anchors.txt` for `doc` and `ref` directives.
    * `download`: scan `download` directives for external content, into `docs` folder, producing `download/download.txt` folders.
    * `toc`: scan `toc` directives, producing nav structure for use with `mkdocs.yml` file
    
    ```
    mkdocs_translate scan
    ```

5. To bulk convert all content from ``rst`` to ``md``:
   
    ```
    mkdocs_translate rst source/**/*.rst
    ```
   
6. Review this content you may find individual files to fix.

    Some formatting is easier to fix in the `rst` files before conversion:
   
    * Indention of nested lists in ``rst`` is often incorrect, resulting in restarted numbering or block quotes.
  
    * Random ``{.title-ref}`` snippets is a general indication to simplify the rst and re-translate.

    * Anchors or headings with trailing whitespace throwing off the heading scan, resulting in broken references

6. Convert a single file:
   
   ```
   mkdocs_translate rst source/introduction/license.rst
   ```

7. Bulk convert files in a folder:
   
   ```
   mkdocs_translate rst source/introduction/**/*.rst
   ```

8. To generate out navigation tree:
   
   ```
   mkdocs_translate scan toc
   ```
   
   The output is printed to standard out and may be appended to `mkdocs.yml` file.

### Known limitations

Some things are not supported by pandoc, which will produce ``WARNING:`` messages:

* substitutions used for inline images

* Underlines: replace with bold or italic
  
   ```
   WARNING: broken reference 'getting_involved' link:getting_involved-broken.rst
   ```
   

## Language Translation

Translations are listed alongside english markdown:

* `example.md`
* `example.fr.md`

Using ***pandoc*** to convert to `html`, and then using the [Deepl REST API](http://deepl.com).

4. Provide environmental variable with Deepl authentication key:

   ```
   export DEEPL_AUTH="xxxxxxxx-xxx-...-xxxxx:fx"
   ```

5. Translate a document to french using pandoc and deepl:

   ```
   mkdocs_translate french docs/help/index.md
   ```
   
6. To translate several documents in a folder:

   ```
   mkdocs_translate french docs/overview/*.md
   ```
   
   Deepl charges by the character so bulk translation not advisable.

See ``mkdocs_translate french --help`` for more options.

You are welcome to use  google translate, ChatGPT, or Deepl directly - keeping in mind markdown formatting may be lost.

Please see the writing guide for what mkdocs functionality is supported.

## Local Development

To build and test locally:

1. Clone:

   ```
   git clone https://github.com/jodygarnett/translate.git translate
   ```

2. Install requirements:
   ```
   cd translate
   pip3 install -r mkdocs_translate/requirements.txt
   ```

2. Install locally:
   ```
   pip3 install -e .
   ```

Debugging:

1. Recommend troubleshooting a single file at a time:

   ```rst
   mkdocs_translate rst docs/index.rst
   ```
   
2. Compare the temporary files staged for pandoc conversion:

   ```
   bbedit docs/index.rst docs/index.md target/convert/index.tmp.html target/convert/index/tmp.md
   ```
   
3. To turn on logging during conversion:

   ```bash
   mkdocs_translate --log=DEBUG translate.yml rst
   ```

Pandoc:

1. The pandoc plugin settings are in two constants:

   ```python 
    md_extensions_to =
        'markdown+definition_lists+fenced_divs+backtick_code_blocks+fenced_code_attributes-simple_tables+pipe_tables'
    md_extensions_from =
        'markdown+definition_lists+fenced_divs+backtick_code_blocks+fenced_code_attributes+pipe_tables'
   ```

2. The pandoc extensions are chosen to align with mkdocs use of markdown extensions, or with post-processing:

   | markdown extension   | pandoc extension       | post processing |
   |----------------------|------------------------|-----------------|
   | tables               | pipe_tables            |                 |
   | pymdownx.keys        |                        | post processing |
   | pymdownx.superfences | backtick_code_blocks   | post processing | 
   | admonition           | fenced_divs            | post processing |
   
3. To troubleshoot just the markdown to html conversion:
   
   ```bash
   mkdocs_translate internal_html manual/docs/contributing/style-guide.md
   mkdocs_translate internal_markdown target/contributing/style-guide.html

   diff manual/docs/contributing/style-guide.md target/contributing/style-guide.md
   ```
 
## Configuration

For geoserver or core-geonetwork (or other projects following maven conventions) no configuration is required.

To override configuration on command line add `-concfig <file.yml>` before the command:

```bash
mkdocs_translate --config translate.yml rst
```

The file `mkdocs_translate/config.yml` file contains some settings (defaults are shown below):

* `deepl_base_url`: "https://api-free.deepl.com"
      
   Customize if you are paying customer.
      
* `project_folder`: "."
   
   Default assumes you are running from the current directory.

* `rst_folder`: "source"

* `docs_folder`: "docs"

* `build_folder`: "target"
   
   The use of "target" follows maven convention, python projects may wish to use "build"

* `docs_folder`: "docs"
   
   mkdocs convention.
   
* `anchor_file`: 'anchors.txt'
  
* `upload_folder`: "translate"
  
   Combined with ``build_folder`` to stage html files for translation (example:  `build/translate`)
   
* `convert_folder`: "convert"

   Combined with ``build_folder`` for rst conversion temporary files (example:  `build/convert`).
   Temporary files are required for use by pandoc.
   
* `download_folder`: "translate"
   
   Combined with ``build_folder`` to retrieve translation results (example:  `build/translate`)
   Temporary files are required for use by pandoc.

* `substitutions`: dictionary of `|substitutions|` to use when converting config.py rst_epilog common substitutions.
  
  ``` 
  project: GeoServer
  author: Open Source Geospatial Foundation
  copyright: 2023, Open Source Geospatial Foundation
  project_copyright: 2023, Open Source Geospatial Foundation
  ```
  
* The built-in substitutions for  `|version|` and `|release|` are changed to `{{ version }}` and `{{ release }}``
  variables for use with `mkdocs-macros-plugin` variable substitution:
  
  Use `mkdocs.yml` to define:
  ```
  extra:
    homepage: https://geoserver.org/
    version: '2.24'
    release: '2.24.2'
  ```

* `extlinks`: dictionary of config.py extlinks substitutions.
   
   To convert sphinx-build config.py:
   
   ```
    extlinks = { 
       'wiki': ('https://github.com/geoserver/geoserver/wiki/%s', None),
       'user': ('https://docs.geoserver.org/'+branch+'/en/user/%s', None),
       'geos': ('https://osgeo-org.atlassian.net/browse/GEOS-%s','GEOS-%s')
    }
   ```
    
   Use config.yml (note use of mkdocs-macros-plugin for variable substitution:
   ```
   extlinks:
       wiki: https://github.com/geoserver/geoserver/wiki/%s
       user: https://docs.geoserver.org/{{ branch }}/en/user/%s
       geos: https://osgeo-org.atlassian.net/browse/GEOS-%s|GEOS-%s
       download_release: https://sourceforge.net/projects/geoserver/files/GeoServer/{{ release }}/geoserver-{{ release }}-%s.zip|geoserver-{{ release }}-%s.zip
   ```
  