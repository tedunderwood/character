Experiment on gender balance and genre
======================================

This subfolder contains scripts and data used to explore the question of whether changes in gender balance in fiction can be explained by fluctuations in the amount of "genre fiction" in our collection.

We explored this question only in a quick and loose way, to see if there was some grossly visible pattern. The short answer: no, there wasn't. But that negative result shouldn't be over-interpreted. There's not a whole lot of fiction explicitly tagged by genre in HathiTrust before the 1990s. Part of the reason is that genre tagging was done by different people, across a long span of time; we know that volumes published before 1960 are less likely to have been tagged by genre.

Also the concept of "genre fiction" is itself very unstable. Arguably, all forms of fiction are "genre fiction" in the sense that they belong to some genre. But in this subfolder we've worked provisionally with a definition that we take as loosely equivalent to the popular sense of the term, which is,

That a work of genre fiction is any volume tagged by catalogers with one of the following terms:
genrecats = ['suspense', 'adventure', 'western', 'mystery', 'detective', 'science fiction', 'fantasy', 'horror', 'gothic', 'romance', 'pulp']

Given that definition, there's not a whole lot in the HathiTrust collection before 1990:
![Fraction of genre fiction](https://github.com/tedunderwood/character/blob/master/genre_experiment/fraction_of_genre_fiction.jpeg)