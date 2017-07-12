transform_data
==============

Ideally, all the analysis for characters would run in a single script operating on the raw texts of volumes. In reality, that's impossible for a number of reasons -- copyright issues, processing would take days, etc.

So there are in practice two stages of transformation before you get to the data used for visualization in the article. First, we run BookNLP on the texts themselves to produce lists of characters in json files.

But those are still very big files, and not easy to manipulate. For instance, you would have to pair a document id to metadata in order to get the publication date for a character.

So we create an intermediate data representation, tabular rather than json, and including date since we almost always need to refer to that.

**jsontotable5.py** is the workhorse script that does the transformation. Note that this file will require two wordlists located in the /lexicons directory of the repo; you will have to rewrite the paths in the code. More crucially, you will need your own jsons, because we haven't shared our original json data yet. At present, this script is more for replicability -- doing your own experiment -- than for reproducing our results.

The two scripts that select subsets (**select_authgender_subset** and **select_balanced_subset**) allow you to reproduce the process that created the character-level metadata in the **metadata** directory. You could alter, for instance, the median character length.

The two scripts that get optimums (**get_authgender_optimums** and **get_decade_optimums**) are an admittedly kludgy part of the modeling process, dealing with hyperparameter optimization. The scripts in **train_models/reproduce_character_models.py** try four different hyperparameters for each sample, and record all the results in **dataforR.** The get-optimum scripts here then select the best hyperparameter for each sample, to produce the results that I actually visualized. But the original grids are also preserved, so you can inspect the consequences of hyperparameter optimization.

The more elegant way to do this would be to build the optimization routine into **reproduce_character_models.py** so a separate step is not required.

