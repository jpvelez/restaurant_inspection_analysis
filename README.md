## Question

This analysis tries to answer a simple question: do Chicago restaurants that the City's health inspection 
have a lower rating on Yelp? 

## Steps Taken 
Here are the steps taken to answer that question:

1) Got [food inspection data](https://data.cityofchicago.org/Health-Human-Services/Food-Inspections/4ijn-s7e5)
from the City of Chicago's data portal.

  * `food_inspections.csv`: csv of food inspection data, as of 7/9/2012.


2) Cleaned the food inspection data, and loaded it into sqlite database.

  * `food_inspection.db`: sqlite3 db used for analysis. Created with the following cmd: 
  `sqlite3 food_insection.db`

  * `create_db.py`: loads food_inspection.csv into new inspection_raw table. 

    - for inspections in inspection_raw, converts inspection datetimes into date objects, removes inspections where business license id seems to refer to different establishments ('problem licenses') , and chooses a single facility_type for businesses with multiple facility types.  

    - loads cleaned food inspections into new table inspections_clean


