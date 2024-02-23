# Development

<div class="grid cards" markdown>

-   [Release History](release.md)

</div>

## Local Development

To build and test locally:

1.  Clone:

    ``` bash
    git clone https://github.com/jodygarnett/translate.git translate
    ```

2.  Install requirements:

    ``` bash
    cd translate
    pip3 install -r mkdocs_translate/requirements.txt
    ```

3.  Install locally:

    ``` bash
    pip3 install -e .
    ```

## Debugging

1.  Recommend troubleshooting a single file at a time:

    ``` bash
    mkdocs_translate migrate source/index.rst
    ```

2.  Compare the temporary files staged for pandoc conversion:

    ``` bash
    bbedit source/index.rst docs/index.md build/migrate/index.tmp.html build/migrate/index.tmp.md
    ```

3.  To turn on logging during migrating a file:

    ``` bash
    mkdocs_translate --log=DEBUG migrate source/index.rst
    ```

4.  To troubleshoot indexing when scanning a single document:

    ``` bash
    mkdocs_translate --log=DEBUG scan index --TEST source/index.rst
    ```

    The index information is sent to standard out (rather than added to a **`anchor.txt`** file.

5.  To troubleshoot downloads when scanning a single document:

    ``` bash
    mkdocs_translate --log=DEBUG scan download --TEST source/index.rst
    ```

    The download information is sent to standard out (rather than a **`download.txt`** file.

## Pandoc

1.  The pandoc plugin settings are in two constants:

    ``` python
    md_extensions_to =
        'markdown+definition_lists+fenced_divs+backtick_code_blocks+fenced_code_attributes-simple_tables+pipe_tables'
    md_extensions_from =
        'markdown+definition_lists+fenced_divs+backtick_code_blocks+fenced_code_attributes+pipe_tables'
    ```

2.  The pandoc extensions are chosen to align with mkdocs use of markdown extensions, or with post-processing:

    | markdown extension   | pandoc extension     | post processing |
    |----------------------|----------------------|-----------------|
    | tables pymdownx.keys | pipe_tables          | post processing |
    | pymdownx.superfences | backtick_code_blocks | post processing |
    | admonition           | fenced_divs          | post processing |

3.  Language translation depends on conversion to and from html. To troubleshoot just the markdown to html conversion:

    ``` bash
    mkdocs_translate internal_html docs/contributing/style-guide.md
    mkdocs_translate internal_markdown build/convert/contributing/style-guide.html

    diff docs/contributing/style-guide.md build/convert/contributing/style-guide.md
    ```

    Langauge conversion uses ``text/html`` to avoid internationalization of content distributing markdown formatting.
