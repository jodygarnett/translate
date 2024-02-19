# Migrate

## Preflight

1.  Use init to create **`docs`** directory and copy over non **`rst`** files (such as images and sample data).

    ``` bash
    mkdocs_translate init
    ```

2.  To effectively migrate content the sphinx-build rst docs are scanned to collect information about the anchors, headings and downloads.

    ``` bash
    mkdocs_translate scan
    ```

3.  Optional: You can run these scans independently:

    ``` bash
    mkdocs_translate scan downloads.
    ```

4.  Optional: To troubleshoot an individual file, the resulting `ex` can be sent to standard out:

    ``` bash
    mkdocs_translate scan download --test source/setup/index.rst
    ```

5.  The following is produced during preflight scans:

    ``` text
    docs/setup/download/download.txt
    build/anchors.txt
    ```

## Content Migration {: #migrate }

Format conversion from ***sphinx-build*** reStructuredText files to ***mkdocs*** Markdown content.

1.  To bulk convert all content from **`rst`** to **`md`**:

    ``` bash
    mkdocs_translate migrate
    ```

2.  Review this content you may find individual files to fix.

    Some formatting is easier to fix in the **`rst`** files before conversion:

    -   Indention of nested lists in **`rst`** content is often incorrect, resulting in restarted numbering or block quotes.
    -   Random `{.title-ref}` snippets is a general indication to simplify the rst and re-translate.
    -   Anchors or headings with trailing whitespace throwing off the heading scan, resulting in broken references

3.  Convert a single file:

    ``` bash
    mkdocs_translate migrate source/introduction/license.rst
    ```

4.  Bulk convert files in a folder:

    ``` bash
    mkdocs_translate migrate source/introduction/**/*.rst
    ```

5.  To generate out navigation tree:

    ``` bash
    mkdocs_translate scan toc
    ```

    The output is printed to standard out and may be appended to **`mkdocs.yml`** file.

## Known limitations

Some things are not supported by ***pandoc***, which will produce `WARNING:` messages:

-   Substitutions used for inline images

-   Underlines: replace with bold or italic

        WARNING: broken reference 'getting_involved' link:getting_involved-broken.rst
