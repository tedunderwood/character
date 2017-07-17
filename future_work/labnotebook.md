labnotebook
===========

July 17, 2017
-------------

I didn't think it would make much difference whether we generated gender_probabilities.tsv using one model or four different models, assigned to different slices of time. But it really did make a difference, significantly increasing the correlation between weighted_diff and date, as well as weighted_diff and mean_prestige.

Also note that the absolute value of weighted_diff is very dependent on the L2 regularization used in the model, so if you're going to break the timeline into segments, and want them to be comparable, it becomes important to use the same regularization.