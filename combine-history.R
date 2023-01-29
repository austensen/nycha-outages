# One-off script for prepping 2022 data for ANHD
# TODO: improve quality checks, improve scraper for running on shorter periods and avoid/detect incomplete scrapes

library(tidyverse)
library(fs)
library(lubridate)

history_cols <- cols(
  development_name = col_character(),
  building_number = col_double(),
  address = col_character(),
  interruptions = col_character(),
  planned = col_character(),
  report_date = col_datetime(format = ""),
  end_date = col_datetime(format = ""),
  outage_duration = col_character(),
  buildings_impacted = col_double(),
  units_impacted = col_double(),
  population_impacted = col_double()
)

# Assuming we don't have any overlapping periods in the scraped data
all_history <- path("data") |> 
  dir_ls(recurse=TRUE, glob="*/history.csv") |> 
  map_dfr(function(file) {
    read_csv(file, col_types = history_cols)
  })

# Get a quick sense of any periods we're clearly missing
all_history |> 
  count(date = date(report_date), name = "outages") |> 
  ggplot() +
  aes(x = date, y = outages) +
  geom_col() +
  coord_flip() +
  scale_x_date(date_breaks = "1 months")

# See if we're completely missing any specific days
scraped_dates <- all_history |> 
  distinct(date(report_date)) |> 
  pull()

all_dates <- seq(ymd('2022-01-01'), ymd('2022-12-31'), by = '1 days')

# For some reason these dates always fail when scraping. 
setdiff(all_dates, scraped_dates) |> as_date()
# > "2022-10-20" "2022-11-15"

write_csv(all_history, path("data/nycha-outages_2022.csv"))
