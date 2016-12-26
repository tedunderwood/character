sources of error
================

Any project working with more than a few hundred books is going to make inferences that could lead to error. But we can try to assess the level of error, and check whether it's distributed in a way that might have produced the patterns we see in the data.

In this project, for instance, many of our inferences about gender are based on names and honorifics (Mr, Mrs, Sir, Lady, Baroness, etc). The gendering of a name is a cultural construct; it may vary over time. (See, e.g., Ashley Wilkes.)

Some of the tools we used (i.e., GenderID.py, by Baird and Blevins) are explicitly designed to reflect changes in the gendering of names.

BookNLP, on the other hand, doesn't explicitly compensate for historical change. But Bamman checked manually to see whether its level of error was varying significantly over time.

![Precision and recall for BookNLP](https://github.com/tedunderwood/character/blob/master/error/50years.pdf)

We don't feel that those variations are likely to explain away the patterns we have seen in the data. To double-check this, we also counted pronouns in the Chicago corpus, and compared that trajectory to the number of words BookNLP had assigned to feminine characters.

![Precision and recall for BookNLP](https://github.com/tedunderwood/character/blob/master/error/pronouncheck.jpeg)

The correlation of those two curves is very reassuring.

It's also true that BookNLP will tend to miss first-person narrators; if women writers in the 1950s and 60s were particularly likely to write first-person narrators, who tended to be women, that might explain why fictional women seem to be missing in the period. But we checked the distribution of first-person pronouns across author gender and date, and find no suspicious signal there.

We also considered [sources of error in our metadata, detailed in another folder of the repo.](https://github.com/tedunderwood/character/tree/master/metadata).

In short, there are lots of sources of error here, but we don't think they can collectively explain why women lose a fourth of the space on the page they had possessed in the nineteenth century.
