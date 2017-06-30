Research on characterization
============================

Repo containing code and data for research on characterization published as "The Transformation of Gender in English-Language Fiction, 1780-2007," Ted Underwood, David Bamman, and Sabrina Lee, 2017. 

The original texts of many volumes are under copyright, and couldn't be shared even if the size limits of this repository permitted. So we are sharing derived data, plus metadata which would allow a researcher to retrieve those original texts from HathiTrust Research Center.

The most complete derived data (that we can legally share) are tabular representations of the words associated with individual characters: chartable18c19c.tsv and chartablepost1900.tsv. At 4GB total, these are too big for this repository and will be made available elsewhere. (Dataverse and/or institutional repo.) They include words from dialogue as well as words grammatically associated with character names, but the dialogue is not used in most of the subsequent analysis here. (In these tables, words used in dialogue are distinguished by the prefix "said-.")

Much of the analysis of publishing trends in the first part of the article can be reproduced using **filtered_fiction_metadata.csv** in the **metadata** subdirectory.

To reproduce models is a bit more involved. Most of the modeling was run on a subset of 84,000 characters balanced to have (where possible) 2000 characters with masculine names and 2000 characters with feminine names for each decade. (It's not possible in the late 18c; note also that 1780-1799 have been aggregated and treated as a single decade.) Characters were selected so that the median description length for a character was as close as possible to 54 words for both genders, in each decade. If you want to replicate the selection process itself, you would need to run **select_balanced_subset.py** in the **tranform_data** directory.

Alternatively, you could work with the **character_subset.tar.gz** provided here, unpack that, and run **reproduce_character_models.py** in the **train_models** subdirectory. See that script for usage instructions.

Right now all the data provided in this repo is aggregated by year; we have not yet made available word counts broken out by volume or by character name; that will come out with our article, as will a more tightly integrated and replicable codebase. At the moment, the metadata is in /metadata and data is in /yearlysummaries.

blogpost
--------
Scripts used to calculate confidence intervals and plot visualizations in the blog post ["The Gender Balance of Fiction, 1800-2007."](https://tedunderwood.com/2016/12/28/the-gender-balance-of-fiction-1800-2007/)

plot_scripts
------------
Code used to generate visualizations in the final article.

error
-----
A brief discussion of sources of error in the project.

genre_experiment
----------------
Checking to see whether the rise of genre fiction might explain changes in the gender balance of the larger dataset.

metadata
--------
Contains metadata for volumes used in this project, along with a discussion of metadata error. The central metadata file is **filtered_fiction_metadata.csv.**

pubweekly
---------
Data from spot checking Publisher's Weekly to see how far academic libraries diverge from other ways of sampling the past.

transform_data
--------------
Scripts that transform the raw jsons generated by BookNLP into intermediate tabular data files that can be used for analysis and visualization.

yearlysummaries
---------------
Aggregated yearly word counts, broken out by author gender and character gender, and by the grammatical role of the word. They are not broken out *by the word itself*. For more detailed lexical information, right now, you would need to consult the vizdata folder.

vizdata
--------
Metadata and data used in an interactive visualization.
