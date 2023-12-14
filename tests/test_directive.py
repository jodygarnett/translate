import unittest
import mkdocs_translate.translate

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

            Goodbye        
            """

    def test_preprocess_rst_block_directive(self):
        output = mkdocs_translate.translate._preprocess_rst_block_directive( "inline", self.text, "ignore", _callback)
        self.assertTrue('Discussion text' in output)

        output = mkdocs_translate.translate._preprocess_rst_block_directive("inline", self.text, "admonition", _callback)
        self.assertTrue('### Value' in output)

        output = mkdocs_translate.translate._preprocess_rst_block_directive("inline", self.text, "code-block", _callback)
        self.assertTrue('caption=caption' in output)

    def test_figure_directive(self):
        process = mkdocs_translate.translate._block_directive_figure("test.rst", "images/example.png", {}, None, "   ")
        self.assertEqual(3, len(process.splitlines()),"single line");
        self.assertTrue('example.png' in process)

        process = mkdocs_translate.translate._block_directive_figure("test.rst", "images/example.svg", {}, "caption content", "   ")
        self.assertTrue('example.svg' in process)
        self.assertTrue('caption content' in process)
        self.assertEqual(4, len(process.splitlines()), "single line");

        caption = """caption
        
        legend information:
        * one
        * two
        """
        process = mkdocs_translate.translate._block_directive_figure("test.rst", "/figure/diagram.svg", {}, caption, "   ")
        self.assertTrue('diagram.svg' in process)
        self.assertTrue('caption content' in process)
        self.assertTrue('.. note::' in process)
        self.assertEqual(7, len(process.splitlines()), "single line");


if __name__ == '__main__':
    unittest.main()