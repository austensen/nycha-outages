# NYCHA Outages

NYCHA regularly updates a [web page](https://my.nycha.info/Outages/Outages.aspx) that displays information about service outages for heat/water, electric, elevators, and gas that are planned, ongoing, or recently resolved. This web scraper extracts the data from all of these tables and saves the results in a SQLite database.

Thanks to Steve Giordano ([@steve52](https://github.com/steve52)) for his help on this project.

## morph.io

This web scraper is set up on [morph.io](morph.io) to run once a day and update a SQLite database that is publicly available for download and accessible via API. 

[NYCHA Outages on morph.io](https://morph.io/austensen/nycha-outages)


## Running the scraper locally

You can use Docker to get everything set up and run the scraper. From this directory run:

```
docker-compose build
docker-compose run app
```

## Data dictionary

| column_name | description |
| --- | --- |
| development_name | Name of NYCHA development |
| building_number | Number of building within NYCHA development. If `NULL`, then entire development is affected |
| address | Street address of building within NYCHA development |
| gas_lines | The gas lines affected by gas service outage |
| interruptions | List of services affected by interruption (Ex. "Heat", "Hot Water", etc.) |
| planned | List of values ("Planned", "Unplanned") corresponding to services listed in `interruptions` column |
| reported_scheduled | The date (and time) when the service outage was reported, or for planned outages,the date the outage was was scheduled for |
| gas_restored_on | The "Est. Completion" date that the gas outage. If `NULL`, then status is "In Progress" |
| restoration_time | The number of hours for the service to be restored |
| status | The status of the service outage. The source of values for this column depend on the table that the record originates from on the website. For the "Current" tab the "Status" column is used directly (Ex. "NYCHA Staff Assigned", "NYCHA Staff Working", etc.), for the "Restored in the last 24 hours" tab it will always be "Restored", for the "Upcoming planned outages" tab it will always be "Planned", and for the "Gas" tab the value comes from the "Est. Completion" column and will either be "In Progress" or `NULL`. |
| buildings_impacted | The number of buildings that are impacted by the service outage |
| units_impacted | The number of units that are impacted by the service outage |
| population_impacted | The number of people that are impacted by the service outage |
| imported_on | The datetime that the web scraper was run and the data was imported. |
