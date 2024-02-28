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
        process = mkdocs_translate.translate._preprocess_rst_block_directive("docker.rst", text, 'only',mkdocs_translate.translate._block_directive_only)

        indent: list[int] = indentation(process)
        self.assertEqual(indent[1], indent[3] - 3, "admonition indent")
        self.assertEqual(indent[2], -1)
        self.assertEqual(indent[3], indent[5] - 3, "parsed-literal indent")
        self.assertEqual(indent[4], -1)


    def test_preprocess_list_table(self):
        """
        Test list-table detection of grid-table complexity.
        """
        simple_table_rst = """
.. list-table::
   :widths: 20 80
   :header-rows: 1
   
   * - Module Name
     - Human readable name of the module, this links to a popup containing the full details and messages of the module
   * - Module ID
     - The internal package name of the module
   * - Available
     - Whether the module is available to GeoServer.
       
       A database extension requiring a third-party database driver to be installed would not be available for use.
   * - Enabled
     - Whether the module is enabled in the current GeoServer configuration
   * - Component
     - Functional component provided by the module.
   * - Version
     - The version of the installed module
   * - Message (popup)
     - Status message such as what Java rendering engine is in use, or the library path if the module/driver is unavailable
    """
        process = mkdocs_translate.translate._preprocess_rst_block_directive("docker.rst", simple_table_rst, 'list-table', mkdocs_translate.translate._block_directive_list_table)
        self.assertTrue( "* - Message" not in process)

    def test_preprocess_list_table_blanks(self):
        """
        Test list-table detection of grid-table complexity.
        """
        simple_table_rst = """
.. list-table::


   * - Module Name
   
     - Human readable name of the module, this links to a popup containing the full details and messages of the module
     
   * - Module ID
   
     - The internal package name of the module
     
"""
        process = mkdocs_translate.translate._preprocess_rst_block_directive("docker.rst", simple_table_rst,
                                                                             'list-table',
                                                                             mkdocs_translate.translate._block_directive_list_table)
        self.assertTrue( "* - Module ID" not in process)

    def test_preprocess_list_table_bolds(self):
        """
        This use of bold term can trip up cell detection when * bullet points are used, rather than - bullet points.
        """
        simple_table_rst = """
.. list-table::


   * * **Module Name**

     * Human readable name of the module, this links to a popup containing the full details and messages of the module

   * * Module ID

     * The internal package name of the module

"""
        process = mkdocs_translate.translate._preprocess_rst_block_directive("docker.rst", simple_table_rst,
                                                                             'list-table',
                                                                             mkdocs_translate.translate._block_directive_list_table)
        self.assertTrue("* * **Module Name**" not in process)


    def test_preprocess_list_table_empty_content(self):
        """
        List tables with no content may be missing the white space seperator expected for content matching.
        """
        simple_table_rst = """
.. list-table::

   * - Term
     - Definition
   * - Empty
     - 
   * - Missing
     -
   * - Fin
     - Done
"""
        process = mkdocs_translate.translate._preprocess_rst_block_directive("docker.rst", simple_table_rst,
                                                                             'list-table',
                                                                             mkdocs_translate.translate._block_directive_list_table)
        self.assertTrue("* - Fin" not in process)

    def test_preprocess_list_table_problem(self):
        """
        List tables with no content may be missing the white space seperator expected for content matching.
        """
        rst_example = """
#. Click :guilabel:`Add a new style` and choose the following:

   .. list-table:: 
      :widths: 30 70
      :header-rows: 0

      * - Name:
        - `image_example`
      * - Workspace:
        - `No workspace`
      * - Format:
        - `MBStyle`
"""
        process = mkdocs_translate.translate._preprocess_rst_block_directive("docker.rst", rst_example,
                                                                             'list-table',
                                                                             mkdocs_translate.translate._block_directive_list_table)
        self.assertTrue("* - Format:" not in process)

    def test_list_table_scan(self):
        block ="""   * - **Info**
     - **Example**
     - **Description**
   * - Operating system
     - Linux Mint 18
     - Name of the operating system and the used version
   * - Uptime
     - 08:34:50
     - Up time of the system
"""
        self.assertEqual("pipe-table", mkdocs_translate.translate._list_table_scan(block) )

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