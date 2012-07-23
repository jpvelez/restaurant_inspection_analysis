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
    t = 2.1766, df = 120.181, p-value = 0.03147
    alternative hypothesis: true difference in means is not equal to 0 
    95 percent confidence interval:
    0.01720489 0.36364112 
    sample estimates:
    mean of x mean of y 
    3.621673  3.431250 

    ```

## Findings 

This analysis found two things:

1. There is a modest difference (of .19) in the mean Yelp ratings of Chicago restaurants that passed city inspection (3.62) 
and those that failed (3.43).

2. This difference in Yelp ratings is statistically significant. If we assume that there is actually no 
difference in the mean Yelp ratings of the two restaurant groups, there is a 3% probability (p = 0.031) that the observed 
difference of .19 is due to random chance. That satisfies our confidence level of 95% - it is really unlikely that the observed
result is due to chance.

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

**Why use a random sample of Chicago restaurants?**

1. The first reason I chose to use a sample of Chicago restaurants is because there is no definitive dataset of Chicago restaurants 
that includes both their health inspection history and Yelp rating. These two variables were available in different datasets, each
of which had a different number of unique restaurants - 6342 in the inspection dataset, ~5700 on Yelp. Therefore, any analysis
performed on this data would necessarily be working with sample of the total restaurant population - those unique restaurants that
showed up in both datasets.

2. The second reason is due to the challenge of getting Yelp data. Yelp's api has a rate limit of 100 requests per day, so it would have
taken approximately two months to get all the data necessary. Instead of waiting, I chose to analyze a representative sample of this
dataset. 

To make sure my sample was in fact representative, I randomized the list of inspected restaurants I used to query the Yelp api. That
way, every Yelp api call would return a random sample of the total population of restaurants that appeared both in Yelp and in the
inspections dataset. The more api calls I made, the larger the sample size would be, but it would still be random with every call.

I used python's random.shuffle function to randomize the restaurant list. As far as I could glean from StackOverflow posts, this function
provides 'good-enough' randomness for lists with only a few thousand items.

I made api calls for the first **900 of 6342** restaurants in the randomized list.

3. The final reason is that matching restaurants in the inspection dataset to restaurants on Yelp proved challenging, so I ended up
getting only a subset of restaurants that showed up in both datasets - in other words, a sample of a sample. 

To understand why, I will elaborate on the method I used to match restaurants: I searched for restaurants on Yelp using restaurant names 
and addresses from the inspection dataset. Each of these searches returned a list of 10 restaurants that Yelp thought were relevant 
to the search query. So now I had a set of up to 10 Yelp restaurants associated with a restaurant from the inspection dataset, and I had to find find 
the matches. Some of the time, none of Yelp restaurants matched the inspection restaurant. 45% of the time, however, the Yelp list did
contain a matching restaurant, and it was always the first item in the list, according to a hit rate test I ran on 20 queries. 

To find find matching restaurants, then, I decided to compare the address of the inspection restaurant with that of the first restaurant 
in the returned Yelp list. I found 415 matches out of 900 api calls, so **n = 415** for the analysis. That's 4.4% of the unique restaurants
in the inspection dataset, a large enough sample to answer the question.

I was concerned that my method might be disproportionately finding matches for certain types of restaurants, which could bias the analysis. 
So I spot-checked the restaurant names I used in the hit rate test. Initially it looked like fast food restaurants were being matched
at lower rates than the rest, but this initial pattern did not hold up to closer inspection, suggesting that my method was finding
positive matches in a fairly random fashion.

I was also concerned about false matches, so inspected every one of the 415 matches I found. Only 7 out of 415 matches, or 1.6%, were
clearly false or ambiguous matches. This number was small enough that I did not remove these false/ambiguous restaurants from the
analysis dataset.


**Why did you need to use a t-test to answer the question?**

To answer the question, it was not enough to find the mean Yelp ratings for restaurants that passed and failed their most recent 
canvass inspections. Why? It is always possible that an observed effect - in this case the difference between means - is due to 
random chance. So to be confident in our findings, we need need to quantify how likely it is that the observed difference between 
means of ~0.6 is due to chance alone. In other words, we need to use a statistical hypothesis test, and a t-test is a type of hypothesis
test that is appropriate for comparing means.
