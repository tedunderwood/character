metadata for character research
===============================

**merged_fiction_metadata** lists 110,041 volumes used in this project, stretching from 1800 to 2007.

There is no authoritative master list of "all English-language fiction from 1700 to the present." So scholars who want to do research at scale have to construct their own list.

Doing that by hand might take several decades. University libraries have not reliably tagged all volumes of fiction as "fiction"; you would have to actually check, book by book.

We have adopted a probabilistic solution. Using the texts of volumes, as well as existing metadata, we made reasonably good guesses about genre, and assembled a list of works *likely to be* fiction.

That means the list will contain errors: a certain number of volumes that are actually nonfiction.

The list also includes works in translation. Volumes are dated by date of publication, which is not guaranteed to be the date of *first* publication. We have made an effort to remove duplicates, and books published long after the death of the author. But you will still find works like *The Thousand and One Nights* that were not composed in the period 1800-2007.

There is a separate line for each volume, and the column **volid** always contains a HathiTrust Volume Identifier. The column **docid** contains a code that can be used to identify the *work,* i.e., the story in question -- which may include more than one volume, especially before 1900. If the story includes only one volume this will be identical to the **volid**.

**authgender** is author gender, which will be either m, f, or u (unknown or other). These codes should be understood as probabilistic inferences about a conventional public role, not as claims about the truth of identity. They are based for the most part on names and honorifics, but about 10% of the volumes in the dataset were also corrected by reference to metadata manually produced at Chicago, Stanford, or Illinois.

The number of volumes tagged "u" does steadily increase across time, because academic libraries bought a growing number of works translated from other languages, and our gender-inference software often confesses uncertainty about those names.

