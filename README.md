Research on characterization
============================

Repo containing code and data for research on characterization to be published as 

Ted Underwood, David Bamman, and Sabrina Lee, "The Transformation of Gender in English-Language Fiction," *Cultural Analytics*,  2018. 

The original texts of many volumes are under copyright, and couldn't be shared even if the size limits of this repository permitted. So we are sharing derived data, plus metadata which would allow a researcher to retrieve those original texts from HathiTrust Research Center.

In a perfect world, a single script would take the analysis all the way from raw data to finished visualization with the push of a button. 

This is, however, a sprawling project that developed over the course of two years. The underlying data expanded and changed several times while we were working. The analysis is mostly done in Python, and the final stage of visualization in R. So there are admittedly some rough edges to reproducibility here: readers who want to reproduce images will usually have to retrace several steps.

If you want to reproduce a specific figure,
------------------------------------------
or understand how it was produced, it may be simplest to start with the **images** folder--which contains the images used as figures, with links to the scripts that produced each one.

If you want to understand the underlying data,
----------------------------------------------
A good initial starting place is the [**error**](https://github.com/tedunderwood/character/tree/master/error) folder in this repository, which describes and documents some likely sources of error.

If you actually want to get at the raw data for your own purposes, the most complete derived data (that we can legally share) are tabular representations of the words associated with individual characters: character_table_18c19c.tsv and character_table_post1900.tsv. At 4GB total, these are too big for this repository and will be made available separately in the Cultural Analytics Dataverse. The tables include words from dialogue as well as words grammatically associated with character names, but the dialogue is not used in most of the subsequent analysis here. (In the tables, words used in dialogue are distinguished by the prefix "said-.")

Much of the analysis of publishing trends in the first part of the article can be reproduced using **filtered_fiction_metadata.csv** in the **metadata** subdirectory. The scripts to reproduce that analysis are under **/plot_scripts**; the most important is **gender_plots.py**.

We also used data from the Chicago Text Lab as a contrastive touchstone in several places, but we have only provided a very high-level (yearly) summary of that data here. Contact Hoyt Long or Richard So for more information.

If you want to reproduce predictive modeling,
---------------------------------------------
Most of the modeling was run on a subset of 84,000 characters balanced to have (where possible) 2000 characters with masculine names and 2000 characters with feminine names for each decade. (Total numbers are slightly lower in the late 18c; note also that 1780-1799 have been aggregated and treated as a single decade.) Characters were selected so that the median description length for a character was as close as possible to 54 words for both genders, in each decade. The data we used is in the top level of this repo repo as **balanced_character_subset.tar.gz.**

If you want to reproduce the selection process itself, you would need to run **select_balanced_subset.py** in the **tranform_data** directory. Alternatively, you could work with the **balanced_character_subset.tar.gz** provided here (which is the subset of 84,000 we actually used). Unpack that, and run **reproduce_character_models.py** in the **train_models** subdirectory. See that script for usage instructions.

If you want to explore the gendering of specific words,
-------------------------------------------------------
as we do in figures 11-15, you have two options. An [interactive visualization constructed by Nikolaus Parulian](http://ec2-35-165-215-214.us-west-2.compute.amazonaws.com/dataviz/genderviz) allows you to explore online. Alternatively, you can edit the code in the scripts for figures 10-14 available under **/plotscripts/rplots** or simply write your own code to visualize the data in **dataforR/diff_matrix.csv**, which reports the yearly difference between normalized frequencies for men and women.

Brief descriptions of subdirectories.
======================================
The five most important subdirectories are listed first, then alphabetically.

plot_scripts
------------
Code used to generate visualizations in the final article. This may be the first place to look for options to reproduce or tweak particular figures. Generally there is an initial transformation in Python, which generates a file in **dataforR**. Then a file in **plot_scripts/rplots** does the final visualization in R/ggplot2.

dataforR
--------
Holds the final stage of data, immediately before visualization in R. In particular, this includes a **diff_matrix** that can be used to explore the gendering of individual words.

transform_data
--------------
Scripts that transform the raw jsons generated by BookNLP into intermediate tabular data files, and then select characters from those files for modeling.

train_models
------------
Scripts for predictive modeling. To reproduce figures 7, 9, or 10, you would need to start here.

metadata
--------
Contains metadata for volumes used in this project, along with a discussion of metadata error. The central metadata file is **filtered_fiction_metadata.csv.**

alphabetic hereafter:
---------------------

bestsellergender
----------------
Some data on bestsellers, used in one figure.

blogpost
--------
Scripts used to calculate confidence intervals and plot visualizations in the blog post ["The Gender Balance of Fiction, 1800-2007,"](https://tedunderwood.com/2016/12/28/the-gender-balance-of-fiction-1800-2007/) 2016. Mostly deprecated now.

chicago
-------
A terse, high-level summary of character data from the Chicago Novel Corpus. Note that the  Chicago dataset has expanded and changed since we used it in 2015.

error
-----
A brief discussion of sources of error in the project.

future_work
------------
Further analysis of the data, not included in the published article, or fully documented yet.

genre_experiment
----------------
Checking to see whether the rise of genre fiction might explain changes in the gender balance of the larger dataset. Not directly used in the article version; was displaced by pubweekly, which answered a similar question.

images
------
Images used in the article, with notes on sourcing.

lexicons
--------
Stoplists and other data files, mostly used in transformation of dialogue, which doesn't turn out to be crucial in our final article.

oldcode
-------
deprecated

post22hathi
-----------
Yearly summaries, mostly not used directly in the final analysis, except for post22_character_data.csv.

pre23hathi
----------
Yearly summaries, mostly not used directly in the final analysis, except for pre23_character_data.csv.

pubweekly
---------
Data from spot checking Publisher's Weekly to see how far academic libraries diverge from other ways of sampling the past.

vizdata
--------
Metadata and data used in an interactive visualization.

yearlysummaries
---------------
Aggregated yearly word counts, broken out by author gender and character gender, and by the grammatical role of the word. This is mostly deprecated; I don't think this data is used directly in the current article-reproduction workflow.
