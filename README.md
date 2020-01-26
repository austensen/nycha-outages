# NYCHA Outages

NYCHA regularly updates a [web page](https://my.nycha.info/Outages/Outages.aspx) that displays information about service outages for heat/water, electric, elevators, and gas that are planned, ongoing, or recently resolved. This project scrapes the data from all of these tables and saves the results in CSV files.

## Running the scraper

You can use Docker to get everything set up and run the scraper. From this directory run:

```
docker-compose run app
```