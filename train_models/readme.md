train_models
============

To reproduce the predictive modeling in the article, you'll need all these Python scripts. The one you'll probably need to edit is **reproduce_character_models.py**. Right now it has paths specific to one machine; you'll need to edit those paths so they point to the place where you have actually stored character files on your machine.

Once you've done that, you should be able to reproduce particular modeling runs in the article by giving command-line arguments

**decade_grid** reproduces Fig 7

**auth_specific_charpredict_grid** reproduces Fig 9

**predict_authgender** reproduces Fig 10

You may, in reality, find it simpler to write your own code using scikit-learn. The python scripts I have included here are part of a kit that Underwood is reusing in a lot of different projects, and they include layers of complexity that are not really necessary for this particular project. For instance, looking at this with fresh eyes, you'll probably be puzzled that these scripts expect each character to be a separate file, in a folder of 84,000+ files! That's not the obvious way to handle this data. But it's the way these scripts were written, for a different project, and Underwood found it easier to reuse existing code than to write new code from scratch.

This is also why **versatile_trainer.py** accepts a wide range of parameters that are not actually used in this project. It's designed to be *versatile.* Unfortunately, that's not ideal for streamlined reproducibility.