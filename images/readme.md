images
======

Figures used in the article, with some notes on provenance.

Fig1
------
From the blogpost. Produced by [wordsaboutwomenbysource.R](https://github.com/tedunderwood/character/blob/master/plot_scripts/rplots/wordsaboutwomenbysource.R). The Chicago part of this figure will require data from the **chicago** directory.

Fig2
------
From the blogpost. See **gender_plots.py** and **ggplot_scripts.txt** in **plot_scripts.**

Fig3
------
Produced by [hathiwithpubweeklybars.R](https://github.com/tedunderwood/character/blob/master/plot_scripts/rplots/hathiwithpubweeklybars.R), which draws on data produced by **plot_scripts/pubweekly_gender_plots.py.**

Fig4
----
Produced by the Jupyter notebook in the **bestsellergender** subdirectory.

Fig5
------
Produced by [nonfiction_stacked_area.R](https://github.com/tedunderwood/character/blob/master/plot_scripts/rplots/nonfiction_stacked_area.R), which draws on data produced by **plot_scripts/nonfiction_stack_graph.py**.

Fig6
------
From the blogpost. See **gender_plots.py** and **ggplot_scripts.txt** in **plot_scripts.**

Fig7
-----
Produced by [predictiveaccuracybydecade.R](https://github.com/tedunderwood/character/blob/master/plot_scripts/rplots/predictiveaccuracybydecade.R) which draws on data produced by **reproduce_character_models.py** with the command-line argument "decade_grid." You will need to transform the output with **get_decade_optimums.py**. Sorry that's such a pain to reproduce. It was a pain to generate, too!

Fig8
------
Not sure we have included the code for this.

Fig9
----
Produced by [predictiveaccuracybyauthgender.R](https://github.com/tedunderwood/character/blob/master/plot_scripts/rplots/predictiveaccuracybyauthgender.R), which draws on data produced by **reproduce_character_models.py** with the command-line argument "auth_specific_charpredict_grid." You will need to transform the output with **get_authgender_optimums.py**. 

Fig10
--------
Created by [superimpose_author_character.R](https://github.com/tedunderwood/character/blob/master/plot_scripts/rplots/superimpose_author_character.R), which draws on data produced by **reproduce_character_models.py** with the command-line argument "predict_authgender."

Figs 11-15
-----------
These are produced by versions of the same script in the [**rplots** directory.](https://github.com/tedunderwood/character/tree/master/plot_scripts/rplots) Look for any script that begins "Fig" and ends with the words in question. These scripts are easily edited to produce your own images if you have **dataforR/diff_matrix.csv**.
