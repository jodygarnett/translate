import errno
import glob
import logging
import os
import pkgutil
import re
import subprocess
from typing import Callable

import deepl
import yaml

from mkdocs_translate import __app_name__

logger = logging.getLogger(__app_name__)

# global configuration setup by cli._config_callback
config: dict = {}
docs_folder: str = None
rst_folder: str = None
upload_folder: str = None
convert_folder: str = None
download_folder: str = None
anchor_file: str = None

anchors: dict = {}

md_extensions_to = 'markdown+definition_lists+fenced_divs+backtick_code_blocks+fenced_code_attributes-simple_tables+pipe_tables'
md_extensions_from = 'markdown+definition_lists+fenced_divs+backtick_code_blocks+fenced_code_attributes+pipe_tables'


#
# CLI SUPPORT AND CONFIGURATION
#
def load_auth() -> str:
    """
    Look up DEEPL_AUTH environmental variable for authentication.
    """
    AUTH = os.getenv('DEEPL_AUTH')
    if not AUTH:
        raise ValueError('Environmental variable DEEPL_AUTH required for translate with Deepl REST API')

    return AUTH


def load_config(override_path: str) -> dict:
    """
    Load config.yml application configuration.
    :param override_path: Overide config location, or None to use built-in default configuration
    """
    if override_path:
        # override configuration
        with open(override_path, 'r') as file:
            text = file.read()
            return yaml.safe_load(text)
    else:
        # default configuration
        raw = pkgutil.get_data('mkdocs_translate', "config.yml")
        return yaml.safe_load(raw.decode('utf-8'))


def init_config(override_path: str) -> None:
    """
    Initialize using provided config
    :param override_path: Overide config location, or None to use built-in default configuration
    """
    global config
    global docs_folder
    global upload_folder
    global convert_folder
    global download_folder
    global rst_folder
    global anchor_file

    config = load_config(override_path)

    docs_folder = os.path.join(config['project_folder'], config['docs_folder'])
    upload_folder = os.path.join(config['project_folder'], config['build_folder'], config['upload_folder'])
    convert_folder = os.path.join(config['project_folder'], config['build_folder'], config['convert_folder'])
    download_folder = os.path.join(config['project_folder'], config['build_folder'], config['download_folder'])
    anchor_file = os.path.join(docs_folder, config['anchor_file'])

    rst_folder = docs_folder
    if 'rst_folder' in config:
        rst_folder = os.path.join(config['project_folder'], config['rst_folder'])

    if not os.path.exists(docs_folder):
        logger.debug(f"The docs folder does not exist at location: {docs_folder}")
        raise FileNotFoundError(errno.ENOENT, f"The docs folder does not exist at location:", docs_folder)

    if not os.path.exists(rst_folder):
        logger.debug(f"The rst folder does not exist at location: {rst_folder}")
        raise FileNotFoundError(errno.ENOENT, f"The rst folder does not exist at location:", rst_folder)

    logger.debug('--- start configuration ---')
    logger.debug('docs folder: %s', docs_folder)
    logger.debug(' rst folder: %s', rst_folder)
    logger.debug('     upload: %s', upload_folder)
    logger.debug('   download: %s', download_folder)
    logger.debug('    anchors: %s', anchor_file)
    logger.debug('--- end configuration ---')
    return


def load_anchors(anchor_txt: str) -> dict[str, str]:
    """
    load anchors reference of the form:
       reference=/absolut/path/to/file.md#anchor
    """
    if not os.path.exists(anchor_txt):
        logger.warning("Anchors definition file not available - to create run: python3 -m translate index")
        raise FileNotFoundError(errno.ENOENT, f"anchors definition file does not exist at location:", anchor_txt)

    index = {}
    with open(anchor_txt, 'r') as file:
        for line in file:
            if '=' in line:
                (anchor, path) = line.split('=', 1)
                index[anchor] = path[0:-1]

    return index


def init_anchors():
    global anchors
    global anchor_file
    anchors = load_anchors(anchor_file)
    logging.debug("anchors loaded:" + str(len(anchors)))


def collect_path(path: str, extension: str) -> list[str]:
    """
    Collect all the files with an extension from a path.
    If the path is a single file the extension should match.
    """
    files = []
    if '*' in path:
        for file in glob.glob(path, recursive=True):
            if file.endswith('.' + extension):
                files.append(file)
    else:
        if path.endswith('.' + extension):
            files.append(path)

    return files


def collect_paths(paths: list[str], extension: str) -> list[str]:
    """
    Collect all the files with an extension from a list of paths.
    If the path is a single file the extension should match.
    """
    files = []

    for path in paths:
        files.extend(collect_path(path, extension))

    return files


#
# RST INDEX MANAGEMENT AND USE
#
def index_rst(base_path: str, rst_file: str) -> str:
    """
    Scan through rst_file producing doc and ref indexs
    """
    if not os.path.exists(base_path):
        raise FileNotFoundError(errno.ENOENT, f"RST base_path does not exist at location: {base_path}")

    common_path = os.path.commonpath([base_path, rst_file])
    if common_path != base_path:
        raise FileNotFoundError(errno.ENOENT, f"RST base_path '{base_path}' does not contain rst_file: '{rst_file}'")

    with open(rst_file, 'r') as file:
        text = file.read()

    relative_path = rst_file[len(base_path):]
    doc = relative_path
    ref = None
    heading = None
    index = ''

    with open(rst_file, 'r') as file:
        text = file.read()

    lines = text.splitlines()

    for i in range(0, len(lines)):
        line = lines[i]
        if len(line) == 0:
            continue

        if ref:
            heading = scan_heading(i, lines)
            if heading:
                logging.debug(" +- heading:" + heading)
                anchor = ref
                if doc:
                    # reference to doc heading, no need for anchor
                    index += ref + '=' + relative_path + "\n"
                else:
                    index += ref + '=' + relative_path + '#' + ref + "\n"
                index += ref + '.title=' + heading + "\n"
                ref = None

        if doc:
            heading = scan_heading(i, lines)
            if heading:
                logging.debug(" +- page:" + heading)
                index += doc + '=' + relative_path + "\n"
                index += doc + '.title=' + heading + "\n"
                doc = None

        match = re.search(r"^.. _((\w|.|-)*):$", line)
        if match:
            if ref:
                logging.warning("reference " + ref + " defined without a heading, skipped")

            ref = match.group(1)
            logging.debug(" |   ref:" + ref)

    return index


def scan_heading(index: int, lines: list[str]) -> str:
    """
    Detect and return headline

    @return headline, or None
    """
    # Scan line by line for references and headings
    # # with overline, for parts
    h1 = '#############################################################################################################'
    # * with overline, for chapters
    h2 = '*************************************************************************************************************'
    # =, for sections
    h3 = '============================================================================================================='
    # -, for subsections
    h4 = '-------------------------------------------------------------------------------------------------------------'
    # ^, for subsubsections
    h5 = '^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^'
    # “, for paragraphs
    h6 = '"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""'
    h7 = "`````````````````````````````````````````````````````````````````````````````````````````````````````````````"
    h8 = "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
    h9 = "'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''"
    if index >= len(lines) - 1:
        return None  # last line cannot be a heading

    line = lines[index]
    line_length = len(line)
    under = lines[index + 1]
    under_length = len(under)

    if under_length < line_length:
        return None  # not a heading

    if under == h1[0:under_length] or \
            under == h2[0:under_length] or \
            under == h3[0:under_length] or \
            under == h4[0:under_length] or \
            under == h5[0:under_length] or \
            under == h6[0:under_length] or \
            under == h7[0:under_length] or \
            under == h8[0:under_length] or \
            under == h9[0:under_length]:
        return line

    return None


def _doc_title(rst_path: str, doc_link: str) -> str:
    """
    Create a label title, based on a documentation link (using on anchors.txt index)
    """
    resolved_path = _doc_location(rst_path, doc_link)
    # example:
    #   /install-guide/loading-samples.rst=/install-guide/loading-samples.rst
    #   /install-guide/loading-samples.rst.title=Loading templates and sample data
    title_key = resolved_path + '.rst.title'
    if title_key in anchors:
        return anchors[title_key]
    else:
        label = _label(doc_link)
        logger.warning("broken doc '" + doc_link + "' title:" + label)
        return label


def _doc_location(rst_path: str, doc_link: str) -> str:
    """
    Determines absolute path location for link, relative to provided path.

    Do not use as is, mkdocs only works with relative links

    :param rst_path: path of rst file providing the documentation link
    :param doc_link: documentation link (may be absolute or relative)
    :return: absolute path, indicating location relative to docs folder. Used for looking up title.
    """
    if doc_link.startswith("/"):
        return doc_link
    else:
        dir = os.path.dirname(rst_path)
        dir2 = os.path.relpath(dir, rst_folder)
        link_path = os.path.join(dir2, doc_link)
        return '/' + link_path


def _label(link: str) -> str:
    """
    Create a default label, based on a doc link or reference.
    """
    label = link.replace('.rst', '')
    label = label.replace('.md', '')
    label = label.replace('/index', '')
    label = label.replace('-', ' ')
    label = label.replace('_', ' ')
    label = label.replace('/', ' ')
    label = label.title()

    return label


def _ref_title(reference: str) -> str:
    """
    Determines title for reference (using on anchors.txt index)
    :param reference: reference to document or heading
    :return: title for reference
    """
    title_lookup = reference + ".title"

    if title_lookup in anchors:
        return anchors[title_lookup]
    else:
        label = _label(reference)
        logger.warning("broken reference '" + reference + "' title:" + label)
        return label


def _ref_location(reference: str) -> str:
    """
    Determines absolute path#anchor for reference (using on anchors.txt index)
    :param reference: reference to document or heading
    :return: absolute path, indicating location relative to docs folder. Used to determine a relative path.
    """
    if reference in anchors:
        return anchors[reference]
    else:
        link = reference + "-broken.rst"
        logger.warning("broken reference '" + reference + "' link:" + link)
        return link


def _ref_path(rst_path: str, reference: str) -> str:
    """
    Generate a relative link for the provided reference.
    """
    logging.debug("ref: " + reference)
    ref_location = _ref_location(reference)

    rst_location = os.path.relpath(os.path.dirname(rst_path), rst_folder)
    if ref_location.startswith("/"):
        ref_location = ref_location[1:]

    logging.debug("   reference: " + rst_location)
    logging.debug("    absolute: " + ref_location)

    link = os.path.relpath(ref_location, rst_location)

    logging.debug("    relative: " + link)
    return link


#
# RST PANDOC CONVERSION
#
def convert_rst(rst_file: str) -> str:
    """
    Use pandoc to convert rich-structured-text file to markdown file for mkdocs
    :param md_file: Markdown file path
    :return: markdown file path
    """
    if not os.path.exists(rst_file):
        raise FileNotFoundError(errno.ENOENT, f"RST file does not exist at location:", rst_file)

    if rst_file[-4:] != '.rst':
        raise FileNotFoundError(errno.ENOENT, f"Rich-structued-text 'rst' extension required:", rst_file)

    # file we are generating
    md_file = rst_file.replace(".rst", ".md").replace(".txt", ".md")

    if md_file.startswith(rst_folder):
        md_file = md_file.replace(rst_folder, docs_folder)

    if 'rst_folder' in config and 'docs_folder' in config and config['rst_folder'] != config['docs_folder']:
        md_file = md_file.replace(config['rst_folder'], config['docs_folder'])

    # temp file for processing
    md_tmp_file = re.sub("^" + config['rst_folder'] + "/", convert_folder + '/', rst_file)
    md_tmp_file = md_tmp_file.replace(".txt", ".md")
    md_tmp_file = md_tmp_file.replace(".rst", ".md")
    md_tmp_file = md_tmp_file.replace(".md", ".tmp.md")

    convert_directory = os.path.dirname(md_tmp_file)
    if not os.path.exists(convert_directory):
        logger.info("Creating conversion directory '" + convert_directory + "'")
        os.makedirs(convert_directory)

    rst_prep = re.sub(r"\.md", r".prep.rst", md_tmp_file)

    logging.debug("Preprocessing '" + rst_file + "' to '" + rst_prep + "'")
    preprocess_rst(rst_file, rst_prep)

    logging.debug("Converting '" + rst_prep + "' to '" + md_tmp_file + "'")

    completed = subprocess.run(["pandoc",
                                #      "--verbose",
                                "--from", "rst",
                                "--to", md_extensions_to,
                                "--wrap=none",
                                "--eol=lf",
                                "-o", md_tmp_file,
                                rst_prep
                                ])
    if completed.returncode != 0:
        print(completed)

    if not os.path.exists(md_tmp_file):
        raise FileNotFoundError(errno.ENOENT, f"Pandoc did not create md file:", md_tmp_file)

    logging.debug("Preprocessing '" + md_tmp_file + "' to '" + md_file + "'")
    postprocess_rst_markdown(md_tmp_file, md_file)
    if not os.path.exists(md_file):
        raise FileNotFoundError(errno.ENOENT, f"Did not create postprocessed md file:", md_file)

    return md_file


def preprocess_rst(rst_file: str, rst_prep: str) -> str:
    """
    Pre-process rst files to simplify sphinx-build directives for pandoc conversion
    """
    with open(rst_file, 'r') as file:
        text = file.read()

    # process toc_tree directive into a list of links
    if '.. toctree::' in text:
        text = _preprocess_rst_toctree(rst_file, text)

    text = _preprocess_rst_block_directive(rst_file, text, 'only', _block_directive_only)
    text = _preprocess_rst_block_directive(rst_file, text, 'include', _block_directive_include)
    text = _preprocess_rst_block_directive(rst_file, text, 'literalinclude', _block_directive_literalinclude)
    text = _preprocess_rst_block_directive(rst_file, text, 'parsed-literal', _block_directive_parsed_literal)
    text = _preprocess_rst_block_directive(rst_file, text, 'figure', _block_directive_figure)

    if ':ref:' in text:
        text = _preprocess_rst_ref(rst_file, text)

    #    if '.. figure::' in text:
    #        text = _preprocess_rst_figure(rst_file,text)

    # strip unsupported things
    if '.. index::' in text:
        text = _preprocess_rst_strip(rst_file, text, 'index')
    if '.. contents::' in text:
        text = _preprocess_rst_strip(rst_file, text, 'contents')

    # gui-label and menuselection represented: **Cancel**
    text = re.sub(
        r":guilabel:`(.*?)`",
        r"**\1**",
        text,
        flags=re.MULTILINE
    )
    text = re.sub(
        r":menuselection:`(.*?)`",
        r"**\1**",
        text,
        flags=re.MULTILINE
    )

    # command represented: ***mkdir***
    text = re.sub(
        r":command:`(.*?)`",
        r"***\1***",
        text,
        flags=re.MULTILINE
    )

    # file path represented: **`path`**

    if ":file:" in text:
        file_pattern: Pattern = re.compile(r":file:`(.*?)`")
        text = file_pattern.sub(
            lambda match: "**`"+match.group(1)+"`**",
            text
        )


    # kbd input represented with as literal text in by mkdocs
    # physical keys represented with +++ctrl+alt+del++
    text = re.sub(
        r":kbd:`(.*?)`",
        r"`\1`",
        text,
        flags=re.MULTILINE
    )

    # very simple literals: `some text` should use ``some text``
    text = re.sub(
        r"(\s)`(\w|\s)*([^`])`([^`])",
        r"\1``\2\3``\4",
        text,
        flags=re.MULTILINE
    )

    # static - rst_epilog stuff from config.py
    if 'substitutions' in config:
        replace: dict[str, str] = config['substitutions']
        for (key, value) in replace.items():
            text = text.replace('|' + key + '|', str(value))

    # dynamic - macros
    if '|version|' in text:
        text = text.replace('|version|', ' {{ version }}')
    if '|release|' in text:
        text = text.replace('|release|', ' {{ release }}')

    # external links
    if 'extlinks' in config:
        extlinks: dict = config['extlinks']
        for key in extlinks.keys():
            ext = ':'+key+':'

            if ext in text:
                definition:str = extlinks[key]
                definition_split = definition.split('|')
                if len(definition_split) == 2:
                    link = definition_split[0]
                    label = definition_split[1]
                else:
                    link = definition_split[0]
                    label = '%s'

                # match :key:`link <url>` first
                ext_reference = re.compile(r':' + key + r':`(.*?)\s+<(.*?)>`')
                text = ext_reference.sub(
                    lambda match: "`" + match.group(1) + " <" + link.replace(r'%s', match.group(2)) + ">`_",
                    text
                )
                # match :key:`<url>` second
                ext_reference = re.compile(r':' + key + r':`(.*?)`')
                text = ext_reference.sub(
                    lambda match: "`" + label.replace(r'%s', match.group(1)) + " <" + link.replace(r'%s', match.group(1)) + ">`_",
                    text
                )

    with open(rst_prep, 'w') as rst:
        rst.write(text)

def _markdown_header(text: str, header: str, value: str) -> str:
    """
    Add a yaml header to the document text.
    """
    if text.startswith('---\n', 0, 5):
        (header, markdown) = text.split('---\n')
        yaml = yaml.safe_load(header)
        dct[header] = value

        return '---\n' + yaml.dump(header) + '\n' + '---\n' + markdown
    else:
        return '---\n' + header + ': ' + value + '---\n' + text


def _preprocess_rst_doc(path: str, text: str) -> str:
    """
    Preprocess rst content replacing doc references with links.
    """
    global anchors

    # doc links processed in order from most to least complicated

    # :doc:`normal <../folder/index.rst>`
    # :doc:`normal <link.rst>`
    # :doc:`normal <link>`
    # `normal <../folder/index.rst>`
    # `normal <link.rst>`
    # `normal <link.rst>`
    text = re.sub(
        r":doc:`(.+?) <(.+?)(\.rst)?>`",
        r"`\1 <\2.rst>`_",
        text,
        flags=re.MULTILINE
    )

    # :doc:`../folder/index.rst`
    # :doc:`simple.rst`
    # `title <../folder/index.rst>`_
    # `title <simple.rst>`_
    document_reference = re.compile(r":doc:`((\w|-|_)*?)(\.rst)?`")
    text = document_reference.sub(
        lambda match: "`" + _doc_title(path, match.group(1)) + " <" + match.group(1) + ".rst>`_",
        text
    )
    return text


def _preprocess_rst_ref(path: str, text: str) -> str:
    """
    Preprocess rst content replacing ref references with links.
    """
    # ref links processed in order from most to least complicated
    # :ref:`normal <link>`
    named_reference = re.compile(r":ref:`(.*?) <((\w|-)*)>`")
    text = named_reference.sub(
        lambda match: "`" + match.group(1) + " <" + _ref_path(path, match.group(2)) + ">`_",
        text
    )

    # :ref:`simple`
    simple_reference = re.compile(r":ref:`((\w|-)*?)\`")
    text = simple_reference.sub(
        lambda match: "`" + _ref_title(match.group(1)) + " <" + _ref_path(path, match.group(1)) + ">`_",
        text
    )

    return text


def _preprocess_rst_toctree(path: str, text: str) -> str:
    """
    scan document for toctree directives to process
    """
    toctree = None
    process = ''
    for line in text.splitlines():
        if '.. toctree::' == line:
            # directive started
            toctree = ''
            continue

        if toctree != None:
            if len(line.strip()) == 0:
                continue
            if line.strip()[0:1] == ':':
                continue
            if line[0:3] == '   ':
                # processing directive
                link = line.strip().replace(".rst", "")
                label = _doc_title(path, link)
                toctree += f"* `{label} <{link}.rst>`__\n"
            else:
                # end directive
                process += toctree + '\n'
                process += line + '\n'
                toctree = None
        else:
            process += line + '\n'

    if toctree != None:
        # end directive at end of file
        process += toctree

    return process


def _to_relative_path(current_file: str, reference: str) -> str:
    """
    Converts sphinx path reference conventions to a relative path:
    
    * Absolute path: Use of leading / indicates path from the root of the document structure (often conf.py location).
      This is converted to a relative apath from current_file location.
    
    * Relative path: relative path from current_file location
    
    return relative path from current file location  
    """
    relative_path = reference.strip();

    if relative_path[0:1] == '/':
        relative_path = relative_path[1:]
        for _ in range(current_file.count('/') - 1):
            relative_path = '../' + relative_path

    return relative_path


def _block_directive_figure(path: str, value: str, arguments: dict[str, str], block: str, indent: str) -> str:
    """
    Map figure to specific markdown formatting to take advantage of css style.
    See writing guide for background information on this choice.
    """

    image = _to_relative_path(path, value)

    raw = indent + '.. code-block:: raw_markdown\n\n'
    raw += indent + '   ![](' + image + ')\n'

    caption: str = None
    legend: str = None
    if block:
        for line in block.splitlines():
            line = line.strip()
            blank: bool = len(line) == 0
            if blank:
                if legend == None:
                    legend = ''
                else:
                    legend += '\n'
            else:
                if caption == None:
                    caption = line
                else:
                    if legend != None:
                        legend += line + '\n'
                    else:
                        caption += line + '\n'

        if caption[0:1] != '*' and caption[-1:] != '*':
            caption = '*' + caption + '*'

        if caption:
            for line in caption.split('\n'):
                raw += indent + '   ' + line + '\n'

        if legend:
            raw += indent + '   \n'
            raw += indent + '.. note::\n\n'
            for line in legend.split('\n'):
                raw += indent + '   ' + line + '\n'

    return raw

    raw += indent + '      include-markdown "' + relative_path + '"\n'
    if 'start-line' in arguments:
        logging.warning(
            'include ' + value + ' directive: start-line option ignored, change rst to start-after which is supported')
    if 'end-line' in arguments:
        logging.warning(
            'include ' + value + ' directive: end-line option ignored, change rst tp end-before option which is supported')

    if block:
        logging.warning('include ' + value + ' directive: invalid use of directive block content')

    if 'start-after' in arguments:
        start = arguments['start-after']
        raw += indent + '      start="' + start + '"\n'
    if 'end-before' in arguments:
        start = arguments['end-before']
        raw += indent + '      end="' + start + '"\n'

    raw += indent + '   %}\n'

    return raw


def _block_directive_parsed_literal(path: str, value: str, arguments: dict[str, str], block: str, indent: str) -> str:
    """
    Treat this as a code-block so it at least shows up as a literal.
    """

    simplified = indent + '.. code-block::'
    if value:
        language = value.strip()
        simplified += ' ' + language + '\n'
    else:
        simplified += ' text\n'

    simplified += indent + '\n'

    if block:
        for line in block.splitlines():
            simplified += indent + '   ' + line + '\n'
    else:
        logging.debug('parsed-literal expects a code block')

    return simplified


def _block_directive_only(path: str, value: str, arguments: dict[str, str], block: str, indent: str) -> str:
    """
    Process only directive into admonition directive to simplify processing for pandoc.
    Special case using snapshot for nightly build.
    """
    admonition = value.strip()
    if admonition == 'snapshot':
        admonition = "Nightly Build"

    if admonition == 'not snapshot':
        admonition = "Release"

    admonition = admonition.title()

    simplified = indent + '.. admonition:: ' + admonition + '\n'
    simplified += indent + '\n'
    if block:
        for line in block.splitlines():
            simplified += indent + '   ' + line + '\n'

    return simplified + '\n'


def _block_directive_include(path: str, value: str, arguments: dict[str, str], block: str, indent: str) -> str:
    """
    Called by _preprocess_rst_block_directive to convert sphinx directive to raw markdown code block.
    """
    relative_path = value.strip();

    if relative_path[0:1] == '/':
        relative_path = relative_path[1:]
        for _ in range(path.count('/') - 1):
            relative_path = '../' + relative_path

    raw = indent + '.. code-block:: raw_markdown\n\n'
    raw += indent + '   {%\n'
    raw += indent + '      include-markdown "' + relative_path + '"\n'
    if 'start-line' in arguments:
        logging.warning(
            'include ' + value + ' directive: start-line option ignored, change rst to start-after which is supported')
    if 'end-line' in arguments:
        logging.warning(
            'include ' + value + ' directive: end-line option ignored, change rst tp end-before option which is supported')

    if block:
        logging.warning('include ' + value + ' directive: invalid use of directive block content')

    if 'start-after' in arguments:
        start = arguments['start-after']
        raw += indent + '      start="' + start + '"\n'
    if 'end-before' in arguments:
        end = arguments['end-before']
        raw += indent + '      end="' + end + '"\n'

    raw += indent + '   %}\n'

    return raw

def _block_directive_literalinclude(path: str, value: str, arguments: dict[str, str], block: str, indent: str) -> str:
    """
    Called by _preprocess_rst_block_directive to convert sphinx directive to raw markdown code block.
    """
    relative_path = value.strip();

    if relative_path[0:1] == '/':
        relative_path = relative_path[1:]
        for _ in range(path.count('/') - 1):
            relative_path = '../' + relative_path
    else:
        if relative_path[0:1] != '.' and '/' in relative_path:
            relative_path = './' + relative_path

    if 'language' in arguments:
        pygments = arguments['language']
    else:
        pygments = ''

    raw =  indent + '.. code-block:: raw_markdown\n'
    raw += indent + '   \n'
    raw += indent + '   ~~~' + pygments + '\n'
    raw += indent + '   {% \n'
    raw += indent + '     include "' + relative_path + '"\n'

    if 'start-line' in arguments:
        logging.warning(
            'literalinclude ' + value + ' directive: start-line option ignored, change rst to start-after which is supported')
    if 'end-line' in arguments:
        logging.warning(
            'literalinclude ' + value + ' directive: end-line option ignored, change rst tp end-before option which is supported')

    if block:
        logging.warning('literalinclude ' + value + ' directive: invalid use of directive block content')

    if 'start-after' in arguments:
        start = arguments['start-after']
        raw += indent + '      start="' + start + '"\n'
    if 'end-before' in arguments:
        end = arguments['end-before']
        raw += indent + '      end="' + end + '"\n'

    raw += indent + '   %}\n'
    raw += indent + '   ~~~\n'

    return raw


def _preprocess_rst_block_directive(path: str, text: str, directive: str,
                                    directive_processing: Callable[..., str]) -> str:
    """
    Scan document for sphinx-build block directive, delegating to directive_processing callable.

    returns processed text
    """
    if '.. ' + directive + '::' not in text:
        # no processing required
        return text

    # ..<directive>:: <directive_value>
    #   <argument>:<value>
    #
    #   directive_content

    directive_value = None
    directive_arguments = None  # arguments while capturing
    directive_content = None  # rst content while capturing

    directive_raw = None
    indent = None  # indent while capturing

    directive_output = None  # directive output

    # processed text
    process = ''
    logging.debug("preprocessing " + directive + ": " + path)
    for line in text.splitlines():
        logging.debug('processing:' + line)
        blank = len(line.strip()) == 0

        if directive_raw == None:
            match = re.search(r"^(\s*)\.\. " + directive + "::(.*)$", line)
            if match:
                # directive started
                directive_raw = line + '\n'

                indent = match.group(1)
                directive_value = match.group(2)
                directive_content = None
                directive_arguments = {}

                logging.debug("    " + directive + ": " + directive_value)
                continue
            else:
                # logging.debug('      scan:'+line)
                process += line + '\n'
                continue
        else:
            indented = len(line) - len(line.lstrip())
            if blank and directive_content is None:
                logging.debug('     blank:' + line)
                # capture content next
                directive_raw += line + '\n'
                directive_content = ''
                continue
            elif line[indented:indented + 1] == ':' and directive_content is None:
                logging.debug('   process:' + line)
                # capture arguments
                directive_raw += line + '\n'
                (ignore, option, value) = line.split(':', 2)
                logging.debug("      " + option + '="' + value + '"')
                directive_arguments[option] = value.lstrip()
                continue
            elif indented > len(indent):
                # directive content
                directive_raw += line + '\n'
                content = line.strip()
                logging.debug('   content:' + content)

                if directive_content is None or directive_content == '':
                    directive_content = content
                else:
                    directive_content += '\n' + content

                continue
            else:
                # end directive
                directive_output = directive_processing(path, directive_value, directive_arguments, directive_content,
                                                        indent)
                process += directive_output

                # process current line
                match = re.search(r"^(\s*)\.\. " + directive + "::(.*)$", line)
                if match:
                    # directive started
                    directive_raw = line + '\n'
                    indent = match.group(1)
                    directive_value = match.group(2)
                    directive_content = None
                    directive_arguments = {}

                    logging.debug("    " + directive + ": " + directive_value)
                    continue
                else:
                    process += line + '\n'

                    # reset state for scanning
                    directive_raw = None
                    indent = None
                    directive_value = None
                    directive_content = None
                    directive_arguments = None

                    continue

    # reached the end of the text content
    # check if we we were in the middle of processing directive
    if directive_raw != None:
        # end directive at end of file
        logging.debug("      rst:\n" + directive_raw)
        directive_output = directive_processing(path, directive_value, directive_arguments, directive_content, indent)
        logging.debug("      out:\n" + directive_output)

        process += directive_output + '\n'

    return process


# def _preprocess_rst_figure(path: str, text: str) -> str:
#    """
#    scan document for figure directive
#    """
#    block = None
#
#    indent = None  # indent while capturing
#    arguments = None # arguments while capturing
#    content = None # content while capturing
#    figure = None  # simplified
#
#    # processed text
#    process = ''
#    logging.debug("preprocessing figure: "+path)
#    for line in text.splitlines():
#        # logging.debug('processing:'+line)
#        blank = len(line.strip()) == 0
#        if block == None:
#           match = re.search(r"^(\s*)\.\. figure::\s*((\w|-|\.)*)$", line)
#           if match:
#              # figure directive started
#              block = line + '\n'
#              indent = match.group(1)
#              image = match.group(2)
#
#              content = None
#              arguments = {}
#              figure = indent + '.. image:: '+image+'\n'
#
#              logging.debug("    figure: " + image)
#              continue
#           else:
#              # logging.debug('      scan:'+line)
#              process += line + '\n'
#              continue
#        else:
#           indented = len(line) - len(line.lstrip())
#           if blank and content == None:
#              logging.debug('     blank:'+line)
#              # capture content next
#              block += line + '\n'
#              content = ''
#              continue
#           elif line.strip()[indented:1] == ':' and content == None:
#              logging.debug('   process:'+line)
#              # capture arguments
#              block += line + '\n'
#              (ignore,option,value) = line.split(':',2)
#              logging.debug("      "+option+'='+value)
#              arguments[option] = value
#              continue
#           elif indented > len(indent):
#              # directive content
#              block += line + '\n'
#
#              if content == '':
#                  logging.debug('   caption:'+line)
#                  caption = line.strip()
#                  print(caption, caption[0], caption[-1])
#                  if caption[0] == '*' and caption[-1] == '*':
#                      content = indent + caption
#                  else:
#                      content = indent + '*'+caption+'*'
#              else:
#                  logging.debug('   legend:'+line)
#                  content += '\n'+indent+line.strip()
#              # figure += indent + line.strip() + '\n'
#              continue
#           else:
#              logging.debug('      done:'+line)
#              # end directive
#              if arguments:
#                  logging.debug('      arguments:'+str(arguments))
#              if content:
#                  logging.debug('      content:'+content)
#
#              logging.debug("rst figure:\n"+block)
#              logging.debug("rst image:\n"+figure)
#              process += figure
#              if content:
#                  process += content + '\n'
#
#              process += '\n' + line + '\n'
#              block = None
#              figure = None
#              indent = None
#              arguments = None
#              content = None
#              continue
#
#    if block != None:
#       # end directive at end of file
#       logging.debug("rst figure:\n"+block)
#       logging.debug("markdown image:]m"+figure)
#       process += figure + '\n'
#
#    return process

def _preprocess_rst_strip(path: str, text: str, directive: str) -> str:
    """
    Scan document and strip indicated block directive.

    This is used to filter out directives such as '.. contents::` that do not have a markdown equivalent.

    Return processed text
    """
    block = None
    process = ''
    for line in text.splitlines():
        if '.. ' + directive + '::' in line:
            # directive started
            block = line
            continue

        if block != None:
            if len(line.strip()) == 0:
                block += line
                continue
            if line.strip()[0:1] == ':':
                block += line
                continue
            if line[0:3] == '   ':
                # processing directive
                block += line
            else:
                # end directive
                logging.debug("strip " + directive + ":" + block)
                process += '\n' + line + '\n'
                block = None
        else:
            process += line + '\n'

    if block != None:
        # end directive at end of file
        logging.debug("strip " + directive + ":" + block)

    return process


def postprocess_rst_markdown(md_file: str, md_clean: str):
    """
    Postprocess pandoc generated markdown for mkdocs use.

    md_file location of markdown file generated by pandoc
    md_clean location to write cleaned markdown contents
    """

    with open(md_file, 'r') as markdown:
        text = markdown.read()

    # process pandoc ::: adominitions to mkdocs representation
    if ':::' in text:
        text = _postprocess_pandoc_fenced_divs(md_file, text)

    if "{.title-ref}" in text:
        # some strange thing where `TEXT` is taken to be a wiki link
        text = re.sub(
            r"\[([^\]]+)]{\.title-ref}",
            r"``\1``",
            text,
            flags=re.MULTILINE
        )

    # review line by line (skipping fenced code blocks)
    clean = ''
    code = None
    code_language = None

    HEADER_ANCHOR = re.compile(r'^# (.*) \{#.*}$')

    for line in text.splitlines():
        match = re.search(r"^(.*)```(.*)$", line)
        if match:
            if code == None:
                # starts code-block
                code_language = match.group(2)
                if "raw_markdown" in code_language:
                    code = ''
                else:
                    code = line + '\n'
            else:
                # ends code-block
                if "raw_markdown" not in code_language:
                    code += line + '\n'

                clean += code
                code = None
                code_language = None
            continue

        # accept code blocks as is
        if code:
            code += line + '\n'
            continue;

        # non-code clean content
        # fix rst#anchor -> md links#anchor
        line = re.sub(
            r"\[(.+?)\]\(((\w|-|/|\.)*)\.rst(#.*?)?\)",
            r"[\1](\2.md\4)",
            line,
            flags=re.MULTILINE
        )

        # fix windows file path duplication
        line = re.sub(
            r"\*\*\\`(.*?)\\`\*\*",
            lambda match: _postprocess_file(match.group(1)),
            line,
            flags=re.MULTILINE
        )


        # Pandoc escapes characters over-aggressively when writing markdown
        # https://github.com/jgm/pandoc/issues/6259
        # <, >, \, `, *, _, [, ], #
        line = line.replace(r'**\`', '**`')
        line = line.replace(r'\`**', '`**')
        line = line.replace(r'\<', '<')
        line = line.replace(r'\>', '>')
        line = line.replace(r'\_', '_')
        line = line.replace(r"\`", "`")
        line = line.replace(r"\'", "'")
        line = line.replace(r'\"', '"')
        line = line.replace(r'\[', '[')
        line = line.replace(r'\]', ']')
        line = line.replace(r'\*', '*')
        line = line.replace(r'\-', '-')
        line = line.replace(r'\|', '|')
        line = line.replace(r'\@', '@')

        # initial header anchor causes conflicts with use of mkdocs-macros-plugin
        match = HEADER_ANCHOR.match(line)
        if match:
            line = '# ' + match.group(1)

        clean += line + '\n'

    if code:
        # file ended with a code block
        clean += code

    # fix macros in URLs
    link_pattern = re.compile(r"\[(.*?)\]\((.*?)\)",flags=re.MULTILINE)
    clean = link_pattern.sub(
        lambda match: '[' + match.group(1) + '](' + _postprocess_link(match.group(2)) + ')',
        clean
    )
    # add header if needed to process mkdocs extra variables
    MACRO = re.compile(r'\{\{ .* \}\}',flags=re.MULTILINE)
    if MACRO.search(clean):
        clean = '---\nrender_macros: true\n---\n\n' + clean

    with open(md_clean, 'w') as markdown:
        markdown.write(clean)

def _postprocess_link(link:str) -> str:
    link = link.replace(r'%7B%7B%20','{{ ')
    link = link.replace(r'%20%7D%7D', ' }}')

    return link

def _postprocess_file(path:str) -> str:
    path = path.replace('\\\\','\\')
    return "**`"+path+"`**"

def _postprocess_pandoc_fenced_divs(md_file: str, text: str) -> str:
    # scan document for pandoc fenced div info, warnings, ...
    admonition = False
    type = None
    ident = ''
    title = None
    note = None
    process = ''
    for line in text.splitlines():
        match = re.search(r"^(\s*):::\s*(\w*)$", line)
        if match and admonition == False:
            # admonition started
            # https://squidfunk.github.io/mkdocs-material/reference/admonitions/
            admonition = True
            indent = match.group(1)
            type = match.group(2)

            # sphinx-build admonition mappings
            # https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html#rst-directives
            if type == 'attention':
                type = 'info'
            if type == 'caution':
                type = 'warning'
            if type == 'danger':
                type = 'danger'
            if type == 'error':
                type = 'failure'
            if type == 'hint':
                type = 'tip'
            if type == 'important':
                type = 'info'
            if type == 'note':
                type = 'note'
            if type == 'tip':
                type = 'tip'
            if type == 'warning':
                type = 'warning'

            # sphinx-build directives mapping to fenced blogs
            # https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html
            if type == 'todo':
                type = 'info'
                title = 'Todo'
                note = ''
            if type == 'admonition':
                type = 'abstract'
                title = ''

            if type == 'deprecated':
                type = 'warning'
                title = 'Deprecated'
                note = ''
            if type == 'seealso':
                type = 'info'
                title = 'See Also'
                note = ''
            if type == 'versionadded':
                type = 'info'
                title = 'Version Added'
                note = ''
            if type == 'versionchanged':
                type = 'info'
                title = 'Version Changed'
                note = ''
            if type == 'versionchanged':
                type = 'info'
                title = 'Version Changed'
                note = ''
            log("process:'" + line + "'")
            log('start:', type, " title:", title)
            continue

        if admonition:
            # processing fenced div
            log("process:'" + line + "'")

            if match and match.group(2) == 'title':
                # start title processing, next line title
                title = ''
                log("start title")
                continue

            if title == '':
                title = line.strip()  # title obtained
                log("title", title)
                if type == 'abstract':
                    # .. admonition:: Explore does not use seperate ::: marker between title and note
                    note = ''
                continue

            if match and note == None:
                # start note processing, next content is note
                note = ''
                log("start note")
                continue

            if match:
                # processing fenced div
                log("fenced div")
                log("  type:", type)
                log("  title:", title)
                log("  note:", note)

                process += indent + '!!! ' + type

                if title != None and title.lower() != type.lower():
                    process += ' "' + title + '"'

                process += "\n\n"
                for content in note.splitlines():
                    process += '    ' + content + '\n'

                process += "\n"

                admonition = False
                type = None
                ident = ''
                title = None
                note = None
                continue

            if note != None:
                if note == '' and line.strip() == '':
                    # skip initial blank line
                    continue
                note += line + '\n'
                log("note:" + line)
                continue

            # unexpected
            logger.error(md_file + ':' + str(process.count('\n')) + ' unexpected ' + str(type) + ':' + str(title))
            # logger.debug("  admonition", admonition)
            # logger.debug("  type", type)
            # logger.debug("  title", title)
            # logger.debug("  note", note)
            # logger.debug(process)
            raise ValueError('unclear what to process ' + str(type) + " " + str(title) + "\n" + md_file)

        else:
            process += line + '\n'

    if admonition:
        # fenced div was at end of file
        logger.error(md_file + ':' + str(process.count('\n')) + ' unexpected:')
        logger.error("  admonition", admonition)
        logger.error("  type", type)
        logger.error("  title", title)
        logger.error("  note", note)
        logger.debug(process)
        raise ValueError(
            'Expected ::: to end fence dive ' + str(type) + ' ' + str(title) + ' ' + str(note) + "\n" + md_file)

    return process


def log(*args):
    if False:
        message = ''
        for value in args:
            message += str(value) + ' '
        print(message)


def convert_markdown(md_file: str) -> str:
    """
    Use pandoc to convert markdown file to html file for translation.
    :param md_file: Markdown file path
    :return: html file path
    """
    if not os.path.exists(md_file):
        raise FileNotFoundError(errno.ENOENT, f"Markdown file does not exist at location:", md_file)

    if not md_file[-3:] == '.md':
        raise FileNotFoundError(errno.ENOENT, f"Markdown 'md' extension required:", md_file)

    upload_folder = config['upload_folder']

    path = re.sub("^docs/", upload_folder + '/', md_file)
    path = path.replace(".en.md", ".en.html")
    path = path.replace(".md", ".html")
    html_file = path

    html_dir = os.path.dirname(path)
    if not os.path.exists(html_dir):
        print("Translation directory:", html_dir)
        os.makedirs(html_dir)

    md_prep = re.sub(r"\.html", r".prep.md", path)

    logging.debug("Preprocessing '" + md_file + "' to '" + md_prep + "'")
    preprocess_markdown(md_file, md_prep)

    logging.debug("Converting '" + md_prep + "' to '" + html_file + "'")
    # pandoc --from gfm --to html -o index.en.html index.md
    completed = subprocess.run(["pandoc",
                                "--from", md_extensions_from,
                                "--to", "html",
                                "--wrap=none",
                                "--eol=lf",
                                "-o", html_file,
                                md_prep
                                ])
    if completed.returncode != 0:
        print(completed)

    if not os.path.exists(html_file):
        raise FileNotFoundError(errno.ENOENT, f"Pandoc did not create html file:", html_file)

    return html_file


def preprocess_markdown(md_file: str, md_prep: str) -> str:
    with open(md_file, 'r') as file:
        text = file.read()

    clean = ''
    code = ''
    admonition = None

    # handle notes as pandoc fenced_divs
    for line in text.splitlines():
        # phase 1: code-block pre-processing
        #
        # cause pandoc #markdown or #text to force to fenced codeblocks (rather than indent)
        if re.match("^```", line):
            if len(code) > 0:
                # print("code-end: '"+line+"'")
                # end code block (so no processing)
                code = ''

            else:
                # print("code-block: '" + line +"'")
                line = re.sub(
                    r"^```(\S+)$",
                    r"```#\1",
                    line,
                    flags=re.MULTILINE
                )
                line = re.sub(
                    r"^```$",
                    r"```#text",
                    line,
                    flags=re.MULTILINE
                )
                code = line[4:]

        # phase 2: process blocks
        if not admonition:
            if '!!! ' in line:
                # print('admonition start  : "'+line+'"')
                admonition = line
            else:
                clean += line + '\n'
        else:
            indent = admonition.index('!!! ')
            padding = admonition[0:indent]

            if len(line) == 0:
                if '\n' in admonition:
                    # print('admonition blank  : "'+line+'"')
                    admonition += line + "\n"
                else:
                    # print('admonition skip   : "'+line+'"')
                    admonition += "\n"
            elif line[0:indent].isspace():
                # print('admonition content: "'+line+'"')
                # use indent level to gather admonition contents
                admonition += padding + line[indent + 4:] + '\n'
            else:
                # print('admonition end    : "'+line+'"')
                # outdent admonition completed
                first_newline = admonition.index('\n')
                last_newline = admonition.rindex('\n')

                title = admonition[indent + 4:first_newline]
                contents = admonition[first_newline:last_newline]

                # output as pandoc fenced_divs
                clean += padding + "::: " + title
                clean += contents
                clean += padding + ":::\n\n"

                # remember to output line that breaks indent level
                admonition = None

                clean += line + '\n'

    with open(md_prep, 'w') as markdown:
        markdown.write(clean)


def convert_html(html_file: str) -> str:
    """
    Use pandoc to convert markdown file to html file for translation.
    :param html_file: HTML file path
    :return: md file path
    """
    if not os.path.exists(html_file):
        raise FileNotFoundError(errno.ENOENT, f"HTML file does not exist at location:", html_file)

    if not html_file[-5:] == '.html':
        raise FileNotFoundError(errno.ENOENT, f"HTML '.html' extension required:", html_file)

    # prep html file for conversion
    html_tmp_file = html_file[0:-5] + '.tmp.html'

    preprocess_html(html_file, html_tmp_file)
    if not os.path.exists(html_tmp_file):
        raise FileNotFoundError(errno.ENOENT, f"Did not create preprocessed html file:", html_tmp_file)

    if html_file[:-8] == '.fr.html':
        md_file = html_file[0:-8] + '.fr.md'
    if html_file[:-5] == '.html':
        md_file = html_file[0:-8] + '.md'
    else:
        md_file = html_file[0:-5] + '.md'

    md_tmp_file = md_file[0:-3] + ".tmp.md"

    completed = subprocess.run(["pandoc",
                                "--from", "html",
                                "--to", md_extensions_to,
                                "--wrap=none",
                                "--eol=lf",
                                "-o", md_tmp_file,
                                html_tmp_file
                                ])
    print(completed)

    if not os.path.exists(md_tmp_file):
        raise FileNotFoundError(errno.ENOENT, f"Pandoc did not create temporary md file:", tmp_file)

    postprocess_markdown(md_tmp_file, md_file)
    if not os.path.exists(md_file):
        raise FileNotFoundError(errno.ENOENT, f"Did not create postprocessed md file:", md_file)

    return md_file


def preprocess_html(html_file: str, html_clean: str):
    with open(html_file, 'r') as html:
        data = html.read()

    # Fix image captions
    #
    #     ![Search field](img/search.png) *Champ de recherche*
    #
    # Clean:
    #
    #    ![Search field](img/search.png)
    #    *Champ de recherche*
    #
    clean = re.sub(
        r'^<p>:: : note ',
        r'<div class="note">\n<p>',
        data,
        flags=re.MULTILINE
    )
    clean = re.sub(
        r'^<p>:: :</p>',
        r'</div>',
        clean,
        flags=re.MULTILINE
    )
    # Fix deepl not respecting <pre><code> blogs using CDATA
    clean = re.sub(
        r'<code><!\[CDATA\[',
        r'<code>',
        clean,
        flags=re.MULTILINE
    )
    clean = re.sub(
        r'\]\]></code>',
        r'</code>',
        clean,
        flags=re.MULTILINE
    )
    with open(html_clean, 'w') as html:
        html.write(clean)


def postprocess_markdown(md_file: str, md_clean: str):
    with open(md_file, 'r') as markdown:
        data = markdown.read()

    # Fix image captions
    #
    #     ![Search field](img/search.png) *Champ de recherche*
    #
    # Clean:
    #
    #    ![Search field](img/search.png)
    #    *Champ de recherche*
    #
    #     data = re.sub(
    #         r"^(\s*)\!\[(.*)\]\((.*)\)\s\*(.*)\*$",
    #         r"\1![\2](\3)\1*\4*",
    #         data,
    #         flags=re.MULTILINE
    #     )
    # fix icons
    data = re.sub(
        r":(fontawesome-\S*)\s:",
        r":\1:",
        data,
        flags=re.MULTILINE
    )
    # fix fence text blocks
    data = re.sub(
        r'^``` #text$',
        r'```',
        data,
        flags=re.MULTILINE
    )
    # fix fenced code blocks
    data = re.sub(
        r'^``` #(.+)$',
        r'```\1',
        data,
        flags=re.MULTILINE
    )
    with open(md_clean, 'w') as markdown:
        markdown.write(data)


def deepl_document(en_html: str, fr_html: str):
    """
    Submit english html file to deepl for translation.
    :param en_html: English html file
    :param fr_html: French html file
    :return: status
    """

    if not os.path.exists(en_html):
        raise FileNotFoundError(errno.ENOENT, f"HTML file does not exist at location:", en_html)

    AUTH = load_auth()

    # prep html file for conversion
    translate_tmp_file = en_html[0:-5] + '.tmp.html'
    print("Preprocssing", en_html, "to", translate_tmp_file)

    preprocess_translate(en_html, translate_tmp_file)

    translator = deepl.Translator(AUTH)

    try:
        # Using translate_document_from_filepath() with file paths
        translator.translate_document_from_filepath(
            translate_tmp_file,
            fr_html,
            source_lang='EN',
            target_lang="FR",
            formality="more"
        )

    except deepl.DocumentTranslationException as error:
        # If an error occurs during document translation after the document was
        # already uploaded, a DocumentTranslationException is raised. The
        # document_handle property contains the document handle that may be used to
        # later retrieve the document from the server, or contact DeepL support.
        doc_id = error.document_handle.id
        doc_key = error.document_handle.key
        print(f"Error after uploading ${error}, id: ${doc_id} key: ${doc_key}")

    except deepl.DeepLException as error:
        # Errors during upload raise a DeepLException
        print(error)

    if not os.path.exists(fr_html):
        raise FileNotFoundError(errno.ENOENT, f"Deepl did not create md file:", fr_html)

    return


def preprocess_translate(html_file: str, html_clean: str):
    with open(html_file, 'r') as html:
        data = html.read()

    # Fix deepl not respecting <pre><code> blogs using CDATA
    data = re.sub(
        r'<code>',
        r'<code><![CDATA[',
        data,
        flags=re.MULTILINE
    )
    data = re.sub(
        r'</code>',
        r']]></code>',
        data,
        flags=re.MULTILINE
    )
    with open(html_clean, 'w') as html:
        html.write(data)
