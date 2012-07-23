## Question

This analysis tries to answer a simple question: do Chicago restaurants that fail city health inspections
have lower ratings on Yelp? 

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


3) Filtered out restaurants inspections from inspection data, selecting only canvass (i.e. routine) inspections for restaurants that were not out of business.

  * `filter_db.py`: creates new table inspection_clean_restaurants from table inspections_clean using SQL query.


4)   Found most recent canvass restaurant inspections.

  * `filter_db.py`: creates new table inspections_clean_restaurants_recent from table inspections_clean_restaurants using SQL query.

5)    Normalized restaurant names and addresses.

  * `recent_restaurant_inspections_normalized.google-refine.tar.gz` - Google Refine project that: 
    - a. normalizes restaurant names by titlecasing them, clustering and renaming chain restaurants, removing 'Inc.' and other corporates from the end of names, and generally rewriting weird names, and 
    - b. normalizes addresses by making street types (i.e. 'Ave') consistent, removing 'Bldg' or 'Suite' from the end of addresses, and other tweaks to make things consistent with Yelp address format.

  * `recent_restaurant_inspections_normalized.csv` - csv dump of Refine project. Loaded into db using this command: 
    ```sh
    csvsql --db sqlite:///food_inspections.db --table inspections_clean_restaurants_recent_normalized --insert recent_restaurant_inspections_normalized.csv
    ```

6)   Randomized (clean, normalized) canvass restaurant inspections. That way, when restaurants are used to query Yelp api, the resulting sample of restaurant yelp+inspection data will be random no matter how much data we get.

  * `randomize_restaurants.py`: randomizes inspections in table inspections_clean_restaurants_recent_normalized using Python's random.shuffle()
    - creates new table inspections_clean_restaurants_recent_normalized_randomized and inserts randomized inspections into it.

7)   Fetched Yelp restaurant data using randomized restaurant inspections.

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

8)   Joined yelp and inspection data.

  * `join_yelp_inspection_data.py`: Only inspection ids, names, and addresses were added to json output. 

    - So this script fetches additional fields - (inspection) results, risk, etc. 

    - It merges them with a selection of yelp values (rating, address, is_closed, etc.) for the first restaurant in every response. 

  * `restaurants_yelp_inspection_nomatch.csv`: the script then saves the merged data to this csv file (sqlite kept chocking on the data.) 

9)   Matched inspection restaurants to yelp restaurants.

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

10)   Analyzed data in R.

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

This analysis found two things:

1. There is a small difference (of .059) in the mean Yelp ratings of Chicago restaurants that passed city inspection (3.636) 
and those that failed (3.576).

2. This difference in Yelp ratings is not statistically significant. Why? If we assume that there is actually no 
difference in the mean Yelp ratings of the two restaurant groups, there is a 35% probability (p = 0.354) that the observed 
difference of ~.06 is due to random chance. That is not a reliable estimate of the hypothesized effect if we adopt a 95% 
confidence interval.

## Justification

To reach these findings, I analyzed a random sample of Chicago restaurants, looking at their most recent canvass inspections
and current Yelp ratings. I analyzed the data with a t-test.

I will now explain why the data I chose to answer my question is appropriate, and why I am confident that I did the data gathering 
and analysis correctly.

**Why look at canvass inspections?**

    In order not to analyze biased inspection outcomes, I wanted to exclude every inspection that wasn't a routine. 
    The city performs a number of different inspections. For example, sanitarians  will sometimes fail a restaurant during a 
    routine (or canvass) inspection, only to pass them a few days later after they've made necessary corrections. 
    Including these inspections would inflate the inspection pass rate of restaurants in the dataset.

    To select only canvass inspections for restaurants, I wrote a pair of SQL queries. I then checked the returned inspections 
    to make sure they were all of the 'canvass' inspection type and restaurant facility type. Some inspections types were no doubt miscoded 
    during data entry, but these errors were probably random, so we can be confident they didn't bias the dataset.

**Why look at recent inspections?**

    Restaurants are supposed to be inspected at least once a year. Though we know over a third of the restaurants in the dataset 
    weren't inspected in over a year, many of them were inspected several times. Because I was unable to get historical Yelp data,
    I needed a single inspection outcome per restaurant in order to create the two comparison groups - pass and fail. 

    Given that the Yelp data is current as of 7/9/2012, and that the inspections all took place within the past 2-3 years, it seemed 
    acceptable to select the most recent inspection for each restaurant, as these inpsections are more likely to have occured during 
    the same timeframe that Yelp users wrote the reviews reflected in each restaurant's star rating.

    I am confident that I was able to extract recent inspections because I wrote an SQL query using a MAX(inspection_date) clause and a 
    GROUP BY (license_no) clause, which returned "largest" i.e. most recent inspection date for each license number, which 
    serves as the unique id of reach restaurant. 
    
    I am confident that the license numbers serve as unique ids because I removed
    a small number of records were the restaurant name and license_no didn't weren't consistent across inspections in create_db.py.
    Removing these problem records didn't bias the data because there were only a dozen or so, and they didn't appear to follow a pattern.

**Why exclude restaurants that food inspectors found to be out of business?**

    I chose to exclude restaurants that had inspection type 'Out of Business' because these restaurants didn't have the 
    pass/fail values needed to run the analysis. It's possible that restaurants that shut down fail inspections more often, and 
    excluding them would thus bias the results. However, by looking at the most recent inspections that resulted in a pass or fail, I was 
    able to include some of these restaurants

    I did not exclude restaurants that Yelp said were out of business, though. Those restaurants still had Yelp ratings, so if they
    also appeared in the recent inspections dataset, it seemed appropriate to include them in the analysis.

**If you could only get back ratings for half the restaurants, how do you know you didn't only get ratings for certain kinds of restaurants?**

**Why a random sample of Chicago restaurants?**

These is no canonical dataset of Chicago restaurants that includes both health inspection history and Yelp rating.


Why should the reader believe you actually got this finding? 
(Because I can argue that I'm looking at the right thing, and that my steps were sound for looking at that thing)
What are the important choices, and why are they the right ones?

- the choice of last inspection
- the way i tried to get data from yelp - random samples, no obvious bias in the hit rate
- the acceptable losses due to unicode encoding, other stuff..
- the use of a t-test to see if small diff was statistically significant


