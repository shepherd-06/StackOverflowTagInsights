Folder `networks` is a collection of 168 Stack Exchange cotagging networks.

The files look as follows.

$ head -5 english_cotagging.csv
-------
,t1,t2,ct
0,1,2,66
1,1,3,50
2,1,4,16
3,1,5,4
-------

Column information:
1. row ID number
2 and 3. Column tag pair IDs
4. The weight of the edge (number of times the two were co-tagged in a question).
