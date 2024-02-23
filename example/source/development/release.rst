Release History
---------------

.. note:: Release |release|
   
   Current release at time of writing

Release 0.9.5
^^^^^^^^^^^^^

Testing with GeoServer documentation migration available at:

* mkdocs: https://jodygarnett.github.io/geoserver/
* sphinx: https://docs.geoserver.org/latest/en/user/

New features:

``mkdocs_translate init``
   Setup `docs` folder with project assets (non :file:`rst` content) such as images and sample files
  

``mkdocs_translate nav``
  Full nav generation from toctree, including glob support

Release 0.9.0
^^^^^^^^^^^^^

Example project, first release shared publicly:

* mkdocs: http://jodygarnett.github.io/translate/

Documentation:

* Sphinx Build project acting as project docs and a test of migration process.
* Writing guide collected from geonetwork manual with both sphinx-build and markdown examples

New features:

``mkdocs_translate scan download``
    Collect `download` directives, using a :command:`mkdocs` hook to stage files from outside the :file:`docs` folder if required.

Release 0.3.0
^^^^^^^^^^^^^

Released alongside GeoNetwork project migration:

* mkdocs: http://docs.geonetwork-opensource.org/
* sphinx: https://geonetwork-opensource.org/manuals/3.12.x/eng/users/index.html

New features:

``mkdocs_translate scan index``
    Collect anchors and headers into an index to support handling of ``doc``, ``ref`` and ``toctree`` directives.

``mkdocs_translate migrate``
    Convert content from :file:`rst` to :file:`md` using :command:`pandoc` using pre and post processing to support any additional
    directives required.

Release 0.1.0
^^^^^^^^^^^^^

Prototype translation between english and french for HNAP manual:

* english: https://jodygarnett.github.io/iso19139.ca.HNAP/search/records/
* french: https://jodygarnett.github.io/iso19139.ca.HNAP/fr/search/records/

New features:

``mkdocs_translate french``
    Transalte document from english to french using deepl API for proof of concept.

``mkdocs_translate internal-html``
    Convert markdown file to html, for internationalization by external service.
    
``mkdocs_translate internal-markdown``
    Convert html file to markdown using pandoc, to restore markdown content after html internationalization.

