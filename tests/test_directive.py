import logging
import mkdocs_translate.translate
import unittest

def _callback(path:str, value:str, arguments: dict, block:str, indent:str) -> str:
    """
    Called by _preprocess_rst_block_directive
    """

    output = indent + '### '+value.strip()
    output += '\n'+indent + "processing: " + path

    for key, value in arguments.items():
        output += '\n'+indent + key+'='+value

    if block:
        output += '\n'+indent+block

    return output

class TestDirective(unittest.TestCase):
    def test_preprocess_rst_block_directive(self):
        text = """
Hello World
===========

Intro text

.. admonition:: Value

   Block

Discussion text

.. code-block:: language
   :caption: caption
   :linenos:

   example code

Goodbye"""
        output = mkdocs_translate.translate._preprocess_rst_block_directive( "inline", text, "ignore", _callback)
        self.assertTrue('Discussion text' in output)

        output = mkdocs_translate.translate._preprocess_rst_block_directive("inline", text, "admonition", _callback)
        self.assertTrue('### Value' in output)

        output = mkdocs_translate.translate._preprocess_rst_block_directive("inline", text, "code-block", _callback)
        self.assertTrue('caption=caption' in output)

    def test_figure_directive(self):
        process = mkdocs_translate.translate._block_directive_figure("test.rst", "images/example.png", {}, None, "   ")
        self.assertEqual(3, len(process.splitlines()),"fenced single line");
        self.assertTrue('example.png' in process)

        process = mkdocs_translate.translate._block_directive_figure("test.rst", "images/example.svg", {}, "caption content", "   ")
        self.assertTrue('example.svg' in process)
        self.assertTrue('caption content' in process)
        self.assertEqual(5, len(process.splitlines()), "fenced two lines");

        block = (
            "caption\n"
            "multiline\n"
            "\n"
            "legend information:\n"
            "* one"
            "* two"
        )

        process = mkdocs_translate.translate._block_directive_figure("test.rst", "/figure/diagram.svg", {}, block, "   ")
        self.assertTrue('diagram.svg' in process)
        self.assertTrue('caption' in process)
        self.assertTrue('multiline' in process)
        self.assertTrue('.. note::' in process)

    def test_preprocess_rst_block_directive_figure(self):
        text = """
#. In a web browser, navigate to ``http://localhost:8080/geoserver``.

   If you see the GeoServer Welcome page, then GeoServer is successfully installed.

   .. figure:: images/success.png

      GeoServer Welcome Page
      
#. This setup allows direct management of the file data shared with the container. This setup is also easy to update to use the latest container.
        """

        process = mkdocs_translate.translate._preprocess_rst_block_directive("docker.rst", text, 'figure', mkdocs_translate.translate._block_directive_figure)
        self.assertTrue('success.png' in process)


    def test_preprocess_rst_only1(self):
        text = """
#. Download the container

   .. only:: not snapshot
   
      .. parsed-literal::

         docker pull docker.osgeo.org/geoserver:|release|

   .. only:: snapshot
   
      .. parsed-literal::
   
         docker pull docker.osgeo.org/geoserver:|version|.x
        """
        process = mkdocs_translate.translate._preprocess_rst_block_directive("docker.rst", text, 'only',                                                                             mkdocs_translate.translate._block_directive_only)
        self.assertTrue('docker pull' in process)

    def test_preprocess_rst_only2(self):
        """
        Test the white space indentation on blank lines is different throwing off detection of the nested block directives
        """
        text = """
#. Run the container

   .. only:: not snapshot

      .. parsed-literal::
         
         docker run \-\-mount type=bind,src=/MY/DATADIRECTORY,target=/opt/geoserver_data -it -p8080:8080 docker.osgeo.org/geoserver:|release|
      
   .. only:: snapshot
   
      .. parsed-literal::
         
         docker run \-\-mount type=bind,src=/MY/DATADIRECTORY,target=/opt/geoserver_data -it -p8080:8080 docker.osgeo.org/geoserver:|version|.x        
        """
        process = mkdocs_translate.translate._preprocess_rst_block_directive("docker.rst", text, 'only',
                                                                             mkdocs_translate.translate._block_directive_only)
        indent: list[int] = indentation(process)
        self.assertEqual(indent[1], indent[3] - 3, "admonition indent")
        self.assertEqual(indent[2], -1)
        self.assertEqual(indent[3], indent[5] - 3, "parsed-literal indent")
        self.assertEqual(indent[4], -1)

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
    unittest.main()