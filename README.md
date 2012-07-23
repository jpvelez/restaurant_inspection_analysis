## Question

This analysis tries to answer a simple question: do Chicago restaurants that the City's health inspection 
have a lower rating on Yelp? 

## Steps Taken 
Here are the steps taken to answer that question:

1. Got [food inspection data](https://data.cityofchicago.org/Health-Human-Services/Food-Inspections/4ijn-s7e5)
from the City of Chicago's data portal.

  * `food_inspections.csv`: csv of food inspection data, as of 7/9/2012.


2.   Cleaned the food inspection data, and loaded it into sqlite database.

  * `food_inspection.db`: sqlite3 db used for analysis. Created with the following cmd: 
  `sqlite3 food_insection.db`

  * `create_db.py`: loads food_inspection.csv into new inspection_raw table. 

    - for inspections in inspection_raw, converts inspection datetimes into date objects, removes inspections where business license id seems to refer to different establishments ('problem licenses') , and chooses a single facility_type for businesses with multiple facility types.  

    - loads cleaned food inspections into new table inspections_clean


3. Filtered out restaurants inspections from inspection data, selecting only canvass (i.e. routine) inspections for restaurants that were not out of business.

  * `filter_db.py`: creates new table inspection_clean_restaurants from table inspections_clean using SQL query.


4. Found most recent canvass restaurant inspections.

  * `filter_db.py`: creates new table inspections_clean_restaurants_recent from table inspections_clean_restaurants using SQL query.

5. Normalized restaurant names and addresses.

  * `recent_restaurant_inspections_normalized.google-refine.tar.gz` - Google Refine project that: 
    - a. normalizes restaurant names by titlecasing them, clustering and renaming chain restaurants, removing 'Inc.' and other corporates from the end of names, and generally rewriting weird names, and 
    - b. normalizes addresses by making street types (i.e. 'Ave') consistent, removing 'Bldg' or 'Suite' from the end of addresses, and other tweaks to make things consistent with Yelp address format.

  * `recent_restaurant_inspections_normalized.csv` - csv dump of Refine project. Loaded into db using this command: 
    ```sh
    csvsql --db sqlite:///food_inspections.db --table inspections_clean_restaurants_recent_normalized --insert recent_restaurant_inspections_normalized.csv
    ```

6. Randomized (clean, normalized) canvass restaurant inspections. That way, when restaurants are used to query Yelp api, the resulting sample of restaurant yelp+inspection data will be random no matter how much data we get.

  * `randomize_restaurants.py`: randomizes inspections in table inspections_clean_restaurants_recent_normalized using Python's random.shuffle()
    - creates new table inspections_clean_restaurants_recent_normalized_randomized and inserts randomized inspections into it.

7. Fetched Yelp restaurant data using randomized restaurant inspections.

  * `get_yelp_restaurants.py`: for each restaurant in table inspections_clean_restaurants_recent_normalized_randomized, calls Yelp search api using that restaurant's (normalized) name and address. 
    - NOTES: Due to Yelp api rate limits, script only gets data for 100 inspection restaurants at a time, and the offset has to be set manually. 
      - The script only saves first 10 businesses in Yelp response, out of a possible 20.
      - Each Yelp response is a json object with a list of up to 10 'business' results. The vast majority should be restaurants, since we're calling the api using restaurant names, but not all. 
      - According to tests in `get_yelp_restaurant_hitrates.xls`, the Yelp response contains a matching restaurant 45% of the time, and it's almost always the first restaurant in the business list.
    - Adds inspection restaurant id, name, and address to each Yelp json response. This is done so yelp data can be joined with inspection data in the following step, using matching addresses.

  * `yelp_restaurants.json`: this is where get_yelp_restaurants.py saves Yelp json response + associated inspection values. Always going to have only 100 responses.

  * `yelp_restaurants_0-<NUM>`: this is every Yelp response gathered so far. Created out of yelp_restaurants.json using the following command: 
  ```sh
  cat yelp_restaurants.json >> cat yelp_restaurants_0-<NUM>.json && mv yelp_restaurants_0-<NUM>.json yelp_restaurants_0-<NUM + 100>.json
  ```

8. Joined yelp and inspection data.

  * `join_yelp_inspection_data.py`: Only inspection ids, names, and addresses were added to json output. 

    - So this script fetches additional fields - (inspection) results, risk, etc. 

    - It merges them with a selection of yelp values (rating, address, is_closed, etc.) for the first restaurant in every response. 

  * `restaurants_yelp_inspection_nomatch.csv`: the script then saves the merged data to this csv file (sqlite kept chocking on the data.) 

9. Matched inspection restaurants to yelp restaurants.

  * Loaded restaurants_yelp_inspection_nomatch.csv into db using this command: 
  ```sh
  csvsql --db sqlite:///food_inspections.db --table restaurants_yelp_inspection_nomatch  --insert restaurants_yelp_inspection_nomatch.csv
  ```

  * On the sqlite3 command line, matched inspection restaurants to yelp restaurants using the following SQL query: 
  ```sql
  SELECT * FROM restaurants_yelp_inspection_nomatch WHERE address=yelp_address;
  ```

  * `restaurants_yelp_inspection_match.csv`: Output table created by above query to this csv file, so data could be read into R

  * `failed_matches.txt`: Short list of spurious matches.

9. Analyzed data in R.

  * `analysis.r`: reads in csv data, finds means for restaurants that passed and failed, and runs t-test on these means to see if the observed difference between the means (of .06) is statistically significant.

  * Here is the t-test result:
    ```r
    Welch Two Sample t-test
    
    data:  rest.pass$yelp_rating and rest.fail$yelp_rating 
    t = 0.928, df = 251.174, p-value = 0.3543
    alternative hypothesis: true difference in means is not equal to 0 
    95 percent confidence interval:
    -0.06726126  0.18712229 
    sample estimates:
    mean of x mean of y 
    3.636364  3.576433
    ```

## Findings 
