# NYCHA Outages

NYCHA regularly updates a [web page](https://my.nycha.info/Outages/Outages.aspx) that displays information about service outages for heat/water, electric, elevators, and gas that are planned, ongoing, or recently resolved. This web scraper extracts the data from all of these tables and saves the results in a SQLite database.

## morph.io

This web scraper is set up on [morph.io](morph.io) to run once a day and update a SQLite database that is publicly available for download and accessible via API. 

[NYCHA Outages on morph.io](https://morph.io/austensen/nycha-outages)


## Running the scraper locally

You can use Docker to get everything set up and run the scraper. From this directory run:

```
docker-compose build
docker-compose run app
```
