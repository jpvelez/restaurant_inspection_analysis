rest = read.csv('restaurants_yelp_inspection_match.csv')

rest.pass = rest[rest$results == 'Pass',]
rest.fail = rest[rest$results == 'Fail',] 

print('Mean Yelp rating for restaurants that passed inspections:')
summary(rest.pass$yelp_rating)

print('Mean Yelp rating for restaurants that failed inspections:')
summary(rest.fail$yelp_rating)

print('Running t-test on means of passed & failed inspections:')
t.test(rest.pass$yelp_rating, rest.fail$yelp_rating)
