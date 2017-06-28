transform_data
==============

Ideally, all the analysis for characters would run in a single script operating on the raw texts of volumes. In reality, that's impossible for a number of reasons -- copyright issues, processing would take days, etc.

So there are in practice two stages of transformation before you get to the data used for visualization in the article. First, we run BookNLP on the texts themselves to produce lists of characters in json files.

But those are still very big files, and not easy to manipulate. For instance, you would have to pair a document id to metadata in order to get the publication date for a character.

So we create an intermediate data representation, tabular rather than json, and including date since we almost always need to refer to that.

**jsontotable5.py** is the workhorse script that does the transformation.