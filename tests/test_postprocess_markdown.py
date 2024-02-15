import logging
import unittest
import mkdocs_translate.translate


class TestPostProcessMarkdown(unittest.TestCase):
    # logging.basicConfig(level=logging.INFO)

    def test_nested_divs(self):
        markdown = """
::: admonition
Explore Device Differences

1.  Different output devices provide limitations in the amount of color information they can portray.

2.  **Explore:** How does changing to a printed map affect the number of classes you can communicate using the current \"pastel\" approach?

    ::: admonition
    Instructor Notes

    The answer is five, but to be really sure four. Read the tool tips to determine fitness for purpose.
    :::
:::
        """
        output = mkdocs_translate.translate._postprocess_pandoc_fenced_divs("inline", markdown)
        self.assertTrue('!!! abstract "Instructor Notes"' in output)

    def test_fenced_divs_title(self):
        markdown = """
## Using your own Data Directory

This will run the container with a local data directory. The data directory will be [mounted](https://docs.docker.com/storage/bind-mounts/) into the docker container.

::: note
::: title
Note
:::

Change [/MY/DATADIRECTORY]{.title-ref} to your data directory. If this directory is empty it will be populated with the standard Geoserver Sample Data Directory.
:::

1.  Make sure you have [Docker](https://www.docker.com/) installed.
"""
        output = mkdocs_translate.translate._postprocess_pandoc_fenced_divs("inline", markdown)
        indent: list[int] = indentation(output)

        self.assertEqual(indent[5], 0, "admonition")
        self.assertEqual(indent[6], -1, "blank")
        self.assertEqual(indent[7], 4, "note")
        self.assertEqual(indent[8], -1, "blank")

    def test_fenced_divs(self):
        markdown = """2.  Download the container:

    ::: admonition
    Nightly Build

    These instructions are for GeoServer {{ version }}-SNAPSHOT which is provided as a [Nightly](https://geoserver.org/release/main) release. Testing a Nightly release is a great way to try out new features, and test community modules. Nightly releases change on an ongoing basis and are not suitable for a production environment.

    ``` text
    docker pull docker.osgeo.org/geoserver: {{ version }}.x
    ```
    :::

    ::: admonition
    Release

    These instructions are for GeoServer {{ release }}.

    ``` text
    docker pull docker.osgeo.org/geoserver: {{ release }}
    ```
    :::

3.  Run the container

    ::: admonition
    Release

    ``` text
    docker run -it -p8080:8080 docker.osgeo.org/geoserver: {{ release }}
    ```
    :::

    ::: admonition
    Nightly Build

    ``` text
    docker run -it -p8080:8080 docker.osgeo.org/geoserver: {{ version }}.x
    ```
    :::

4.  Done!
        """
        output = mkdocs_translate.translate._postprocess_pandoc_fenced_divs("inline", markdown)
        self.assertTrue('!!! abstract "Release"' in output)


def indentation(text:str) -> list[int]:
    """
    Check indentation of provided text, tabs treated as three spaces, blank line marked as -1.
    """
    list = []
    for line in text.split('\n'):
        blank = len(line.strip()) == 0
        if not blank:
            # treat tabs as three spaces
            line = line.replace('\t','   ')
            list.append(len(line)-len(line.lstrip()))
        else:
            list.append(-1)

    return list

if __name__ == '__main__':
    logging.basicConfig(level=Logging.INFO)
    logger = logging.getLogger(mkdocs_translate.__app_name__)
    logger.info("hello world")

    unittest.main()