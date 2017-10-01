# ACMI historical film screening data 
this is a work in progress! also i started this like 2 days ago don't @ me
> ACMI dataset released [here](https://github.com/ACMILabs/historic-film-screenings-data)!
## processing

movie.py:

* cleans/processes acmi-collection-data.tsv and dumps it into a pandas DataFrame for further manipulation
* queries TMDB (The Movie Database) API to fill in info about each movie
* concatenates TMDB info as new columns alongside original dataset

at the moment, unique_tmdb.csv contains a table of all the unique films screened at ACMI + corresponding metadata. the date/time/place of each screening corresponds to the first screening of that film.

from cursory inspection, there are still a number of edge case errors (resulting from mistyped records / inconsistent formatting across datasets)

### to do:

* check release date against screening date to confirm correct identity of TMDB movie match (in case more than 2 movies have the same title)
* copy TMDB info from unique_tmdb.csv to the complete screening dataset
* integrate gender-related TMDB data
* refactor movie.py because it's super messy rn

## visualisation

### to do / in progress:

* general explorable graph with sliders/pivot etc - similar to [Shiny Movie Explorer](http://shiny.rstudio.com/gallery/movie-explorer.html). probably implemented using Bokeh or D3.js