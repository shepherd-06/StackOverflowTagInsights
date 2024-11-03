Co-tagging information for 168 Stack Exchange networks.

$ head -5 beer_cotagging_stats.csv
-------
,tag,ct,cotag,cotag_u
0,1,17,21,13
1,2,65,84,45
2,3,66,93,43
3,4,29,44,26
-------

Column information:
1. row ID number
2. tag ID number
3. the number of times the tag was used
4. the count of tags that have been used as a co-tag with this tag
5. the number of unique cotags (<= column 3 value).
