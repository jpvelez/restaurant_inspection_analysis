import sqlite3
import random
# from YelpApi import YelpApi

conn = sqlite3.connect('food_inspections.db')
c = conn.cursor()

c.execute("SELECT * FROM inspections_clean_restaurants_recent")

recent_restaurant_inspections = c.fetchall()

random.shuffle(recent_restaurant_inspections)

for rest in recent_restaurant_inspections:
    print '%s\t%s, Chicago, IL, %s' % (rest[2].title(), rest[6].title().strip(), rest[7])

# api = YelpApi()
# for rest in recent_restaurant_inspections:
#     full_address = rest[6].title() + ', Chicago, IL, ' + rest[7]
#     api(full_address)
