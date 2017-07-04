plot_scripts
============

Code that generates viz in the final article. In most cases the workflow is:

1. Run a Python script in this main folder. It generates derived data in the **/dataforR** directory at the top level of the repo. Then,

2. Run a visualization script in the **/rplots** subfolder, to generate the final image.

**gender_plots** is code David wrote to do bootstrap resampling for the blog post. Also included here because we're going to use that in the final article.

**ggplot_scripts** are R scripts used in the blogpost.

**pubweekly_gender_plots.py** is code that generates data used in a viz that superimposes a HathiTrust line on error bars from Publishers Weekly. The data it generates goes into the **/dataforR** folder, and then is visualized by **hathiwithpubweeklybars.R** in **/rplots.**

**make_diff_matrix.py** creates a matrix listing, for each of the top 6000 words in character description, the difference between its normalized frequency in description of men and of women. This is stored in **/dataforR/diff_matrix.csv** and used by several scripts in **/rplots**.

rplots
------
Various ggplot scripts used for the final stage of visualization.
