import sqlite3
import random

conn = sqlite3.connect('food_inspections.db')
c = conn.cursor()

c.execute("SELECT * FROM inspections_clean_restaurants_recent_normalized")

recent_restaurant_inspections = c.fetchall()

random.shuffle(recent_restaurant_inspections)

# Print restaurants and addresses. Used to generate shuffled_restaurant_list.txt
# for rest in recent_restaurant_inspections:
#     print '%s\t%s, Chicago, IL, %s' % (rest[2].title(), rest[6].title().strip(), rest[7])
