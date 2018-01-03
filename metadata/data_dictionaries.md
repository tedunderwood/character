data dictionaries
=================

A guide to a couple of key data files.

the character tables
--------------------

The raw character tables in the Dataverse repository (character_table_18c19c.tsv and character_table_post1900.tsv) are tab-separated files with one "character" per line.

**docid** is keyed to **docid** in filtered_fiction_metadata (in the code repository). Note that this will not be a HathiTrust volume ID before 1900. Because multivolume novels were so common in the 19c, I grouped multiple HT volids per docid.

**charname** is the character's most common name, as determined by BookNLP. When a character is referred to by uncommon nicknames, they may be divided into multiple "people."

**charid** is simply docid + | + charname, with I think some provision for disambiguation (by an added asterisk) in cases where the same charname occurs more than once in a novel.

**gender** is the character gender, as determined by BookNLP, mainly from clues in names and honorifics.

**pubdate** is keyed to **inferreddate** in filtered_fiction_metadata, and is not guaranteed to be first publication date. It's rather "earliest attested date for this title in the metadata I had."

**words** are the words BookNLP associated with the character. Words that functioned as modifiers, active verbs, and nouns possessed by the character are not distinguished by any prefix. Verbs of which the character was the object are prefixed with "was-". Words spoken by the character in dialogue are prefixed with "said-". (Yes, I know this is a clunky system.) Dialogue was not actually used in the 2018 article this repository is attached to.

filtered_fiction_metadata
-------------------------

A comma-separated file.

**docid** is an identifier that is sometimes equivalent to volumeID, but sometimes a number invented to link multiple volumes as parts of a single novel.

**volid** is HathiTrust volume ID.

**recordid**, if present, is HT record ID.

**author** is the author of the volumes

**inferreddate** is the earliest date for this title we could find attested in metadata

**birthdate**, if present, is a guess about the author's date of birth. Don't take this as biographical gospel; we often used rules of thumb to guess.

**authgender** is author gender, inferred probabilistically -- so again, not gospel

**enumcron** is a field that HathiTrust uses to distinguish volumes

**title** is what it says on the label



