import sqlite3
import random

conn = sqlite3.connect('../data/food_inspections.db')
c = conn.cursor()

c.execute("DROP TABLE IF EXISTS inspections_clean_restaurants_recent_normalized_randomized")

# Get most recent (normalized) restaurant inspections
c.execute("SELECT * FROM inspections_clean_restaurants_recent_normalized")

recent_restaurant_inspections = c.fetchall()

# Randomize restaurants
random.shuffle(recent_restaurant_inspections)

# Create new table and save randomized restaurants to it
c.execute('''CREATE TABLE inspections_clean_restaurants_recent_normalized_randomized
             (inspection_id int, dba text, aka text, license_no int,
              facility_type text, risk text, address text, 
              zip text, last_inspection_date date, inspection_type text,
              results int, violations text, lat real, long real)''')

for row in recent_restaurant_inspections:
    print 'Adding to db:', row
    c.execute('''INSERT INTO inspections_clean_restaurants_recent_normalized_randomized VALUES
    (?, ?, ?, ?,
     ?, ?, ?, ?,
     ?, ?, ?, ?,
     ?, ?)''', row)
 
conn.commit()
