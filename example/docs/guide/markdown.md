# Markdown

These markdown conventions are carefully constructed for consistent representation of user interface elements, files, data and field input.

| Markdown                     | Directive                  |
|------------------------------|----------------------------|
| **strong**               | gui label, menu selection  |
| `monospace`                | text input, item selection |
| *emphasis*                 | figure (caption)           |
| ***strong-emphasis***  | application, command       |
| **`monospace-strong`** | file                       |

!!! note

    The above conventions are important for consistency and are required by the translation process.
    
    As an example we do not wish to translate keyboard input, so these are represented as monospace text input.

## User interface components

Use `**strong**`to name user interface components for interaction (press for buttons, click for link).

Preview:

> Navigate to **Data --> Layers** page, and press **Add** to create a new layer.

Markdown uses `**strong**`

``` markdown
Navigate to **Data > Layers** page,
and press **Add** to create a new layer.
```

Rich structured text uses `menuselection`and `guilabel`directives:

``` reStructuredText
Navigate to **Data --> Layers** page,
and press **Add** to create a new layer.
```

## Selected input

Use `item` for user selected input, or item in a list or tree:

Preview:

> Select `Basemap` layer.

Markdown uses monospace:

``` markdown
Select ``Basemap``layer.
```

Rich structured text uses monospace:

``` reStructuredText
Select ``Basemap`` layer.
```

## Input text

Use `monospace` for user supplied text input:

Preview:

> Use the **Search** field to enter: `Ocean*`

Markdown uses monospace:

``` markdown
Use the **Search** field enter: ``Ocean*``
```

Rich structured text uses `kbd` directive:

``` reStructuredText
Use the **Search** field to enter: ``Ocean*``
```

## Keypress

Use `key` directive for keyboard keys.

Preview:

> Press `Control-s`to search.

Markdown uses **mkdocs-material** [keys](https://squidfunk.github.io/mkdocs-material/reference/formatting/#adding-keyboard-keys) formatting:

``` markdown
Press ++control+s++ to search.
```

Rich structured text:

``` reStructuredText
Press ``Control-s``to search.
```

## Form input

Use definition list to document data entry. The field names use strong as they name a user interface element. Field values to input uses monspace as user input to type in.

Preview:

> 1.  To login as the GeoServer administrator using the default password:
>
>     User:
>
>     :   `admin`
>
>     Password:
>
>     :   `geoserver`
>
>     Remember me
>
>     :   Unchecked
>
>     Press **Login**.

Markdown: definition lists

``` markdown
1.  To login as the GeoServer administrator using the default password:

    **User**

    :   ``admin``

    **Password**

    :   ``geoserver``

    **Remember me**

    :   Unchecked

    Press **Login**.
```

Rich structured text: list-table

``` reStructuredText
#. To login as the GeoServer administrator using the default password:

   .. list-table::
      :widths: 30 70
      :width: 100%
      :stub-columns: 1

      * - User:
        - ``admin``         * - Password:
        - ``geoserver``         * - Remember me
        - Unchecked

   Press **Login**.
```

## Applications, commands and tools

Use **bold** with *italics* for proper names of applications, commands, tools, and products.

Preview:

> Launch ***pgAdmin*** and connect to the `tutorial` database.

Markdown:

``` markdown
Launch ***pgAdmin*** and connect to the ``tutorial``database.
```

Rich structured text uses `command` directive:

``` reStructuredText
Launch ***pgAdmin*** and connect to the ``tutorial`` database.
```

## Files

Use **bold** with `monospace` for files and folders:

Preview

> See configuration file **`WEB-INF/config-security/config-security-ldap.xml`** for details

Markdown:

``` markdown
See configuration file
**`WEB-INF/config-security/config-security-ldap.xml`**
for details
```

Rich structured text:

``` reStructuredText
See configuration
file **`WEB-INF/config-security/config-security-ldap.xml`**
for details
```

## Links and references

### Internal References

Reference to other section of the document (some care is required to reference a specific heading):

> Authors have access to [translation](../translate/language.md#translate) for initial draft.

Markdown use of relative links and anchor:

``` markdown
Authors have access to [translation](../translate/language#translate) for initial draft.
```

reStructuredText use of `ref` directive:

``` reStructuredText
Authors have access to `translation <../translate/language.rst#translate>`_ for initial draft.
```

### Download of sample file

Sample file included in the documentation:

> Download schema [example.txt](files/example.txt).

Markdown relative link, with text following **bold** with `monospace`file convention above:

``` markdown
Download text [**`example.txt`**](files/example.txt).
```

You may also experiment with mkdocs attr_list to supply a filename:

``` markdown
Download text [**`example.txt`**](files/example.txt) {:download="example.txt"} .
```

reStructured text uses `downlaod` directive:

``` reStructuredText
Download text `example.txt <files/example.txt>`__.
```

### Download of external file {: #download_external }

To include sample file from outside of the documentation tree:

> Open-source [LICENSE.md](download/LICENSE.md)

!!! note

    This functionality is not supported by Material for mkdocs (or any plugin I could find). It is accomplished using the **`download.py`** hook described in [setup](../setup/index.md#download_hook).

To use **`download.py`** hook, create a **`download`** folder to hold staged files

Markdown refers to this folder using a relative link (like normal):

``` markdown
Open-source [**`LICENSE.md`**](download/LICENSE.md)
```

Create **`download/download.txt`** with list of files to stage during ***mkdocs*** build process:

~~~text
{% 
  include "./files/download.txt"
%}
~~~

reStructuredText uses `download` directive with relative path (you may starting leading **`/`** to indicate the root of the documentation **`source`** folder):

``` reStructuredText
Open-source `LICENSE.md <download/LICENSE.md>`__
```

## Icons, Images and Figures

### Icons

Material for mkDocs has extensive [icon support](https://squidfunk.github.io/mkdocs-material/reference/icons-emojis/), for many user interface elements we can directly make use of the appropriate icon in Markdown:

``` markdown
1.  Press the *Validate :fontawesome-solid-check:* button at the top of the page.
```

### Custom icons

Custom icons:

> ![osgeo_mark](img/osgeo_mark.svg){width="20px" height="20px"} Empower everyone with open source geospatial

Material for MkDocs provides support for custom icons:

``` markdown
:osgeo-logo: Empower everyone with open source geospatial
```

Add images to **`overrides/.icons/`** (yes it is a hidden folder):

    overrides/
    - .icons/
      - osgeo/
        logo.svg

reStructuredText does not offer custom icons, the closest is the use of substitutions to "inline" and image.

~~~rst
{% 
  include "./custom_icon_rst.txt"
%}
~~~

!!! warning

    The ***mkdocs_translate*** and ***pandoc*** combo is unable to convert inline images at this time.
    
        [WARNING] Reference not found for 'Key "osgeo_mark"' at build/migrate/guide/markdown.tmp.prep.rst_chunk line 5 column 13

### Figures

Figures are used frequently to allow a caption to describe screen shots and diagrams.

> ![](img/foss4g.svg)
> *Free and Open Source Software for Geospatial*

Markdown handles figures are handled by convention adding emphasized text after each image.

``` markdown
![FOSS4G](img/foss4g.svg)
*Free and Open Source Software for Geospatial*
```

!!! note

    The convention above depends on CSS rules in **`overrides/assets/stylesheets/extra.css`** to provide a consistent presentation:
    
    ~~~css
    {% 
      include "../../overrides/assets/stylesheets/extra.css"
    %}
    ~~~

!!! note

    The official Material for MkDocs answer for [images with captions](https://squidfunk.github.io/mkdocs-material/reference/images/#image-captions) is to use `md_in_html` extension:
    
    ``` markdown
    <figure markdown="span">
      ![FOSS4G](img/foss4g.svg){ scale="25%" }
      <figcaption>Free and Open Source Software for Geospatial</figcaption>
    </figure>
    ```

reStructuredText has a `figure` directive:

``` reStructuredText
.. code-block:: raw_markdown

   ![](img/foss4g.svg)
   *Free and Open Source Software for Geospatial*
```

### Images

Image content:

> ![image](img/foss4g.svg)

Markdown provides inline image syntax.

``` markdown
![](img/foss4g.svg)
```

Use of mkdocs att_list can be used to adjust scale:

``` markdown
![](img/foss4g.svg){ scale="25%" }
```

reStructuredText has an `image` directive:

``` reStructuredText
.. image:: img/foss4g.svg
   :scale: 25%
```

## Tables

Material for MkDocs :squidfunk`data tables <reference/data-tables/>` use pipe-tables approach (supported by both ***mkdocs*** and ***pandoc***):

Leading `` |` tailing ```:

``` markdown
| First Header | Second Header | Third Header |
|--------------|---------------|--------------|
| Content Cell | Content Cell  | Content Cell |
| Content Cell | Content Cell  | Content Cell |
```

Column alignment using ``:``

``` markdown
| First Header | Second Header | Third Header |
|:-------------|:-------------:|-------------:|
| Left         |    Center     |        Right |
| Left         |    Center     |        Right |
```

## Inline content

Use of [mkdocs-include-plugin](https://github.com/mondeja/mkdocs-include-markdown-plugin) provides ability to inline content. Example project uses following **`mkdocs.yml`** setup:

``` yaml
plugins:
  - include-markdown:
      preserve_includer_indent: true
      dedent: true
      comments: false
```

The official Material for mkdocs guidance is to use [snippets](https://squidfunk.github.io/mkdocs-material/setup/extensions/python-markdown-extensions/#snippets) however this did not offer the ability to include code examples and configuration from outside the document tree.

!!! abstract "Reference"

    -   [mkdocs-include-markdown-plugin](https://pypi.org/project/mkdocs-include-markdown-plugin/)
    -   [mkdocs-exclude](https://pypi.org/project/mkdocs-exclude/)

### include content

Inlining a snippet from another file is helpful for material such as disclaimers or statements which are repeated in text.

> Empower everyone with open source geospatial

Here is a snippet to include markdown files inline, requires opening tag `{%` and closing tag `%}`:

~~~markdown
{% 
  include "./include_md.txt"
%}
~~~

!!! note

    Placeholders `{/`and `/}`used to indicate location of `{%`and `%}`in above code example.

Writers can use `include-markdown` with a glob pattern to inline many files, and an option to adjusting header level. Together these two features can be used break up longer pages into more manageable size.

This takes the place of the sphinx-build `include` directive:

~~~rst
{% 
  include "./include_rst.txt"
%}
~~~

!!! note

    You may wish to use the **`txt`** extension for included content. If you wish to use **`md`** extension you can adjust **`mkdocs.yml`** `exclude` or not `not_in_nav` to address warnings.
    
    ``` yaml
    plugins:
      - exclude:
          glob:
            - '**/files/*.md'
    ```

### include config and code

Including configuration and code examples:

> ``` xml
> <CharacterString>da165110-88fd-11da-a88f-000d939bc5d8</CharacterString>
> ```

Use `include`to include normal files, with optional use of start and end markers to capture a snippet, and dedent for appearance.

In this case we are including content into an xml code block to provide syntax highlighting, requires opening tag `{%` and closing tag `%}` within the code block:

~~~markdown
{% 
  include "./include_code_md.txt"
%}
~~~

!!! note

    Placeholders `{/`and `/}`used to indicate location of `{%`and `%}`in above code example.

This takes the place of the sphinx-build `literal-include` directive:

~~~rst
{% 
  include "./include_code_rst.txt"
%}
~~~
