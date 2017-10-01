# ACMI historical film screening data 
i wrote this in like 2 days don't @ me
## processing

movie.py:

* cleans/processes acmi-collection-data.tsv and dumps it into a pandas DataFrame for further manipulation
* queries TMDB (The Movie Database) API to fill in info about each movie
* concatenates TMDB info as new columns alongside original dataset

at the moment, unique_tmdb.csv contains a table of all the unique films screened at ACMI + corresponding metadata.

from cursory inspection, there are still a number of edge case errors (resulting from mistyped records / inconsistent formatting across datasets)

### to do:

* check release date against screening date to confirm correct identity of TMDB movie match (in case more than 2 movies have the same title)
* copy TMDB info from unique_tmdb.csv to the complete screening dataset
* refactor movie.py because it's super messy rn

## visualisation
### to do: