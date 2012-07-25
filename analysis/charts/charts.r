library('ggplot2')

rest = read.csv('../data/restaurants_yelp_inspection_match.csv')

# Filter out canvass inspections that resulted in pass or fail
rest.passfail = rest[rest$results != 'Pass w/ Conditions',]  

# Remove 'Pass w/ Conditions' level from results data
rest.passfail$results = factor(rest.passfail$results)   

# Generate histogram of Yelp ratings for all restaurants 
qplot(yelp_rating, data=rest.passfail, geom='histogram', binwidth=0.5)

# Generate ratrings histogram for pass vs. fail
qplot(yelp_rating, data=rest.passfail, geom='histogram', binwidth=0.5) + facet_grid(~results)

