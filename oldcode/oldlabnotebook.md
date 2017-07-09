character
=========

Scripts used starting in 2016 to finish the character-gender project.

count_characters.py and count_old_characters.py were used to produce

charspacebydoc.csv and charspacebyyear.csv, which aggregate words associated with or spoken by characters in post-23 and pre-23 fiction, respectively.

Then there's the task of producing enriched metadata.

current state
-------------
I lost some work here around Oct 1-2 by not documenting it fully at the time, but the current state of play is that by-document character summaries are located in character_data and pre23_character_data. Those can be paired with character_metadata and pre23_character_metadata, which

creating test data for David
----------------------------

Let's select volumes where there is only one volume per story. Let's select ten per decade. We'll get the pre-1900 volumes from enrichedmetadataDec6. Start in 1780.

We'll get 1900-20 from TARDIS/work/characterdata/originaljsons/20thc_characters2.json.

And after 1920 we'll rely on chicago.json in the same folder.

Oct 12 dedup and condensation
-----------------------------

post22hathi
-----------
Current state of play is

post23 Hathi vols, broken out at the vol level in
character_data.csv
which I have just now renamed

post22_character_data.csv

Complete metadata for that set was in
character_metadata.csv
which I have just renamed

post22_character_metadata.csv

That then passed through a couple of filters:
deduplicate_metadata.py
and
datefilter_metadata.py
to produce a list of volumes that are mostly published within 80 years of their author's birth

now in
datefiltered_post22_meta.csv
when that is fused with
post22_character_data

it produces
filtered_post22_summary.csv
which is the current final product here

Work still to be done: improving author gender ascription in post22_character_metadata

pre23hathi
----------
pre23_character_data
and pre23_character_metadata

get fused by aggregate_old_authgender
to produce
pre23_hathi_summary

chicago
-------
chicago_character_data.csv
and
chicago_metadata.csv
get fused to produce
chicago_summary.csv

Then, in the top level folder,

combine_all_summaries.py does what it says, prodcollated_hathi_summaries.csvucing
collated.summaries.csv

while 
combine_hathi_summaries.py
leaves out chicago,
producing
collated_hathi_summaries.csv

December 16, 2016
-----------------
Rewrote combine_hathi_summaries to work with new metadata (manually corrected for authgender). This produced corrected_hathi_summaries.csv.
