"""
This module provides services written around pandoc for format translation,
and deepl for language translation services.
"""
# message/cli.py

import logging
import os
import shutil
from typing import List
from typing import Optional

import typer
from typing_extensions import Annotated

import mkdocs_translate.translate
from mkdocs_translate import __app_name__, __version__
from .translate import collect_path
from .translate import collect_paths
from .translate import convert_html
from .translate import convert_markdown
from .translate import convert_rst
from .translate import deepl_document
from .translate import init_anchors
from .translate import init_config
from .translate import scan_download_rst
from .translate import scan_index_rst
from .translate import scan_toctree

import yaml

app = typer.Typer(help="Translation for mkdocs content")

logger = logging.getLogger(__app_name__)


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"{__app_name__} v{__version__}")
        raise typer.Exit()


def _log_callback(log: str) -> None:
    logging_format = '%(levelname)s: %(message)s'
    if not log:
        logging.basicConfig(format=logging_format, level=logging.INFO)
    elif 'DEBUG' == log.upper():
        logging.basicConfig(format=logging_format, level=logging.DEBUG)
    elif 'WARNING' == log.upper():
        logging.basicConfig(format=logging_format, level=logging.WARNING)
    elif 'INFO' == log.upper():
        logging.basicConfig(format=logging_format, level=logging.INFO)
    elif 'ERROR' == log.upper():
        logging.basicConfig(format=logging_format, level=logging.ERROR)
    elif 'CRITICAL' == log.upper():
        logging.basicConfig(format=logging_format, level=logging.CRITICAL)
    else:
        logging.config.fileConfig(log)


def _config_callback(config_path: str) -> None:
    init_config(config_path)


@app.command()
def french(
        md_file: Annotated[str, typer.Argument(help="Markdown file path")]
):
    """
    Translate markdown file to french using convert, document and markdown steps.
    """
    html_en = convert_markdown(md_file)

    html_fr = html_en[0:-5] + '.fr.html'
    deepl_document(html_en, html_fr)

    translated = convert_html(html_fr)

    folder = os.path.dirname(md_file)

    md_fr = os.path.normpath(os.path.join(folder, os.path.basename(translated)))

    shutil.copy2(translated, md_fr)

    print(md_fr, "\n")

@app.command()
def scan(
        scan: Optional[str] = typer.Option(
            "all",
            "--scan",
            help="RST scan to perform (all, index, download).",
        ),
        test_rst_file: Annotated[str, typer.Argument(
            help="Test scan a single file, sending output to standard output",
        )] = None
):
    """
    Scan rst files collecting index, download, toc details for migration process.
    """
    check_folders()

    rst_folder = mkdocs_translate.translate.rst_folder

    if test_rst_file:
        if scan.lower() in ("all","index"):
            print(f"\nTest scan anchor and header index: { test_rst_file }\n")
            index_test = scan_index_rst(rst_folder, test_rst_file)
            print("------------------------------")
            if index_test:
                print(index_test, end="")
            print("------------------------------")
        if scan.lower() in ("all","download"):
            print(f"\nTest scan :download: directive: ${ test_rst_file }")
            print("------------------------------")
            download_references: set[str] = scan_download_rst(rst_folder, test_rst_file)
            if download_references:
                print('\n'.join(download_references))
            print("------------------------------")
        return

    rst_glob = rst_folder + "/**/*.rst"

    collected = collect_path(rst_glob, 'rst', True)
    logger.info("Scanning " + str(len(collected)) + " files")

    if scan.lower() in ("all","index"):
        scan_index(collected)
    if scan.lower() in ("all","download"):
        scan_download(collected)

def scan_index( collected: list[str]):
    # configuration settings
    rst_folder = mkdocs_translate.translate.rst_folder
    anchor_path = mkdocs_translate.translate.anchor_file

    index = ''
    for file in collected:
        logger.debug("index: " + file)
        index += scan_index_rst(rst_folder, file)

    anchor_dir = os.path.dirname(anchor_path)
    if not os.path.exists(anchor_dir):
        print("anchors.txt index directory:", anchor_dir)
        os.makedirs(anchor_dir)
    with open(anchor_path, 'w') as anchor_file:
        anchor_file.write(index)
    logger.info("index: "+anchor_path)

def scan_download( collected: list[str] ):
    # configuration settings
    docs_folder = mkdocs_translate.translate.docs_folder
    rst_folder = mkdocs_translate.translate.rst_folder

    downloads: dict[str : set[str]] = dict()
    for file in collected:
        download_references: set[str] = scan_download_rst(rst_folder, file)
        if len(download_references) > 0:
            download_folder = os.path.normpath(os.path.join(os.path.dirname(file), "download"))
            if download_folder.startswith(rst_folder):
                download_folder = download_folder.replace(rst_folder, docs_folder, 1)

            if download_folder in downloads:
                downloads[download_folder].extend(download_references)
            else:
                downloads[download_folder] = download_references

    ## output into docs directory for processing
    for [download_folder, download_references] in downloads.items():
        if not os.path.exists(download_folder):
            logging.info("download folder:" + download_folder)
            os.makedirs(download_folder)

        download_txt_file = os.path.join(download_folder,"download.txt")
        with open(download_txt_file, 'w') as download_file:
            logging.info("download.txt: "+ download_txt_file)
            text = "\n".join(download_references)
            download_file.write(text)
        download_gitiginore = os.path.join(download_folder,".gitignore")
        with open(download_gitiginore, 'w') as gitignore:
            text = "*\n!download.txt"
            gitignore.write(text)

@app.command()
def init(
        rst_path: Annotated[
            List[str], typer.Argument(help="path to rst source folder")] = mkdocs_translate.translate.rst_folder
):
    """
    Init docs directory, copying images and files from rst source folder (excluding rst files for migration).
    """
    rst_folder = mkdocs_translate.translate.rst_folder
    docs_folder = mkdocs_translate.translate.docs_folder
    if not os.path.exists(rst_folder):
        raise FileNotFoundError(errno.ENOENT, f"The rst folder does not exist at location:", rst_folder)


    glob: list[str] = []

    if rst_path:
        # if rst_path provided we are only copying artifacts from a directory
        for path in rst_path:
            if os.path.exists(rst_path):
                if os.path.isdir(path) and path.startswith(rst_folder):
                    glob.append( rst_path + "/**/*" )
                else:
                    logger.warning(rst_folder+" does not contain folder "+path)
            else:
                raise FileNotFoundError(errno.ENOENT, f"RST folder does not exist at location:", path)
    else:
        glob.append(mkdocs_translate.translate.rst_folder + "/**/*")

    # create docs if required
    if not os.path.exists(docs_folder):
        logger.info("Creating docs directory '" + docs_folder + "'")
        os.makedirs(docs_folder)

    traverse_files = collect_paths(glob, 'rst', False)
    for file in traverse_files:
        copy = file.replace(rst_folder, docs_folder,1)
        if os.path.basename(copy) in ['conf.py']:
            continue

        if not os.path.exists(os.path.dirname(copy)):
            os.makedirs(os.path.dirname(copy), exist_ok=True)

        if os.path.isfile(file):
            shutil.copy2(file, copy)
        print(copy)

@app.command()
def nav(
        rst_file: Annotated[str, typer.Argument(
            help="Scan toctree location, defaults to rst source folder.",
        )] = None
):
    """
    Scan rst files collecting toctree structure into a working mkdocs nav tree.
    """
    check_folders()
    init_anchors()

    if rst_file:
        rst_index = rst_file
    else:
        rst_index = mkdocs_translate.translate.rst_folder

    if os.path.exists(rst_index) and os.path.isdir(rst_index):
        rst_index = os.path.join(mkdocs_translate.translate.rst_folder,'index.rst')

    if not os.path.exists(rst_index):
        raise FileNotFoundError(errno.ENOENT, f"RST file to scan for toctree not found at location:", rst_index)

    nav: object = scan_toctree(rst_index)
    print(yaml.dump(nav))


def check_folders():
    """
    Check docs and rst folder exist before doing anything else.
    """
    rst_folder = mkdocs_translate.translate.rst_folder
    docs_folder = mkdocs_translate.translate.docs_folder
    if not os.path.exists(docs_folder):
        raise FileNotFoundError(errno.ENOENT, f"The docs folder does not exist at location:", docs_folder)

    if not os.path.exists(rst_folder):
        raise FileNotFoundError(errno.ENOENT, f"The rst folder does not exist at location:", rst_folder)

@app.command()
def migrate(
        rst_path: Annotated[
            List[str], typer.Argument(help="path to rst file(s)")] = mkdocs_translate.translate.rst_folder,
):
    """
    Convert rst files to markdown using pandoc.

    The rst directives are simplified prior to conversion following our writing guide:
    gui-label, menuselection, file, command
    """
    check_folders()
    init_anchors()

    if not rst_path:
        rst_glob = mkdocs_translate.translate.rst_folder + "/**/*.rst"
        rst_path = [rst_glob]

    for rst_file in collect_paths(rst_path, 'rst', True):
        md_file = convert_rst(rst_file)
        print(md_file)


@app.command()
def internal_html(
        md_file: Annotated[str, typer.Argument(help="Markdown file path")]
):
    """
    Convert markdown file to html using pandoc (some additional simplifications applied).
    This step is used prior to translation.
    """
    file = convert_markdown(md_file)
    print(file, "\n")


@app.command()
def internal_markdown(
        html_file: Annotated[str, typer.Argument(help="HTML file path")]
):
    """
    Convert translated html file back to markdown using pandoc.

    Some additional post-processing applied to clean up formatting harmed during
    translation process.
    """
    file = convert_html(html_file)
    print(file, "\n")


@app.command()
def internal_document(
        en_file: Annotated[str, typer.Argument(help="English HTML upload file path")],
        fr_file: Annotated[str, typer.Argument(help="French HTML download file path")]
):
    """
    Upload en_file for translation to deepl services, the translation is downloaded to fr_file.
    Some preprocess applied to preserve code blocks.
    Requires DEEPL_AUTH environment variable to access translation services.
    """
    deepl_document(en_file, fr_file)


@app.callback()
def main(
        version: Optional[bool] = typer.Option(
            None,
            "--version",
            "-v",
            help="Use debug logging to trace program execution.",
            callback=_version_callback,
            is_eager=True,
        ),
        log: Optional[str] = typer.Option(
            None,
            "--log",
            help="Use logging to trace program execution (provide logging configuration file, or logging level).",
            callback=_log_callback,
            is_eager=True,
        ),
        config: Optional[str] = typer.Option(
            None,
            "--config",
            help="Provide to config file to override built-in configuration.",
            callback=_config_callback,
            is_eager=True,
        )
) -> None:
    """
    Services written around pandoc for format translation,
    and deepl for language translation services.
    """
    return
