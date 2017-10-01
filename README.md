# ACMI historical film screening data 
i wrote this in like 2 days don't @ me
## processing

movie.py:

* cleans/processes acmi-collection-data.tsv and dumps it into a pandas DataFrame for further manipulation
* queries TMDB (The Movie Database) API to fill in info about each movie
* concatenates TMDB info as new columns alongside original dataset

from cursory inspection, there are still a number of edge case errors (resulting from mistyped records / inconsistent formatting across datasets)

### to do:

* check release date against screening date to confirm correct identity of TMDB movie match (in case more than 2 movies have the same title)

## visualisation
### to do: