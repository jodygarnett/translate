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

    def test_directive(self):
        output = mkdocs_translate.translate._preprocess_rst_block_directive( "inline", self.text, "ignore", _callback)
        self.assertTrue('Discussion text' in output)

        output = mkdocs_translate.translate._preprocess_rst_block_directive("inline", self.text, "admonition", _callback)
        self.assertTrue('### Value' in output)

        output = mkdocs_translate.translate._preprocess_rst_block_directive("inline", self.text, "code-block", _callback)
        self.assertTrue('caption=caption' in output)


    def test_sum(self):
        self.assertEqual(sum([1, 2, 3]), 6, "Should be 6")


if __name__ == '__main__':
    unittest.main()