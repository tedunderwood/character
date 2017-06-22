publishers weekly
=================

Data gathered from Publisher's Weekly Digital Archive. 

The codebook originally used to gather data is below. At this point, the thing that matters most is **masterpubweeklydata.csv**.

The code in **munge_raw_data.py** goes through the other data files and makes little format adjustments needed to fuse them into **masterpubweeklydata**, which then gets used elsewhere in the repo.

codebook
--------
There are several resources associated with Publisher's Weekly; getting this one requires a little fishing around; in my library search engine, capitalization and the location of the apostrophe actually mattered!)

In particular, we're sampling titles from the *Record*, a section of the magazine that comes relatively early in the issue in the early portion of the print run, and near the back of the magazine later in the print run.

I only sampled fiction. By 1955 this is marked by a FIC in the record itself; earlier in the run you may have to infer from the title. At points in the print run the record makes a distinction between important stuff (big print), and marginal stuff (small print at the bottom of the page). I included both. I didn't include things that were translated from a language other than English, or where the text had originally been composed/copyrighted *ten years or more before* the date of its appearance in PW.

If we're going to be sampling a lot from PW, I don't recommend trying to get all the info I was recording. I recorded a lot of stuff because I wasn't sure which columns I would need to use. If the pattern had been very subtle, I might have needed information about paper/cloth editions, price, publisher, etc. But really all we need are the columns **date, firstpub, author, title, inhathi,** and **gender.**

Column meanings:

**date** is the year the notice appeared in PW

**firstpub** is the first year the book is reported as copyrighted. Not necessary to do external research for this; often PW itself will report that the book was copyrighted a few years earlier. If this date is more than 9 years earlier than the one in the **date** column I didn't include the book.

**author** lastname, firstnames

**title** I only capitalized first word and proper nouns

**genre** is not listed in PW; I did some casual inference; not clear to me we're going to use this, but conceivable that the Venn diagram of "genre fiction" and "inclusion in Hathi" could be useful later. However, the boundaries of genre fiction are notoriously debatable.

**publisher** I just recorded the firm, and left out "Sons" "& Co" etc

**birthdate** Author's date of birth. This requires an internet search outside PW itself, but it can often be combined with the search to find whether it's "in hathi"

**gender** Coded m/f/u. If only initials are listed, or if the name is e.g. Ashley, an internet search may be needed; in some cases it remains unknown.

**inhathi** I kept a window open for Hathi and searched on author and/or title

**htid** if present; I got this by clicking on the link in Hathi and cutting/pasting the id in the url

**binding** I recorded whatever was said in the record. pap == paper, cl == cloth. If both paper and cloth were listed, I took the cloth edition

**dollars** The price for the binding listed; this is generally the most expensive price listed.

**pseudonym** If one is listed in PW or I discovered one
