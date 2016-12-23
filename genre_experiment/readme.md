Experiment on gender balance and genre
======================================

This subfolder contains scripts and data used to explore the question of whether changes in gender balance in fiction can be explained by fluctuations in the amount of "genre fiction" in our collection.

We explored this question only in a quick and loose way, to see if there was some grossly visible pattern. The short answer: no, there wasn't. But that negative result shouldn't be over-interpreted. There's not a whole lot of fiction explicitly tagged by genre in HathiTrust before the 1990s. Part of the reason is that genre tagging was done by different people, across a long span of time; we know that volumes published before 1960 are less likely to have been tagged by genre.

Also the concept of "genre fiction" is itself very unstable. Arguably, all forms of fiction are "genre fiction" in the sense that they belong to some genre. But in this subfolder we've worked provisionally with a definition that we take as loosely equivalent to the popular sense of the term, which is,

That a work of genre fiction is any volume tagged by catalogers with one of the following terms:

    genrecats = ['suspense', 'adventure', 'western', 'mystery', 'detective', 
    'science fiction', 'fantasy', 'horror', 'gothic', 'romance', 'pulp']

"Mystery" is the largest of those categories. Given our definition, there's not a whole lot in the HathiTrust collection before 1990.

![Fraction of genre fiction](https://github.com/tedunderwood/character/blob/master/genre_experiment/fraction_of_genre_fiction.jpeg)

Since we're talking about less than 5% of the corpus before 1960, it's unlikely that genre fiction by itself could be responsible for the declining prominence of women in fiction 1860-1970. (Unless a *whole* lot of volumes were mistakenly left untagged — and visual inspection suggests that the error, while large, isn't large enough to make that sort of difference.) 

But, for whatever it's worth, here's the gender balance in genre fiction compared to the rest of the collection.

![Gender balance by genre](https://github.com/tedunderwood/character/blob/master/genre_experiment/gender_balance_by_genre.jpeg)

The blue-green line there represents the fraction of characterization devoted to women in volumes *not* tagged with any of the genre categories we defined as "genre fiction." The orange line represents the gender balance in "genre fiction."

The sparse data before 1960 makes it difficult to interpret details here. But we can say, generally, that genre fiction (as defined here, and drawn from university libraries) tends to be more biased toward male characters across the twentieth-century timeline we examined. However, the diachronic changes in genre fiction are not, at first glance, dramatically *different* from changes in the rest of the corpus.

So, in short, the data is sparse, categories are hard to define, and our sample is not absolutely stable across time. But we can say at least that we *didn't* find any evidence that would force us to reject the null hypothesis here: which is that there's no particularly strong causal relationship between "the rise of genre fiction" and changes in the gender balance of 20c fiction.

It remains quite possible that something subtler is happening. The masculinist tropes of suspense and adventure fiction might have pervaded the whole dataset — through writers like Joseph Conrad and Ernest Hemingway — in a way that wouldn't become visible explicitly as "genre fiction."