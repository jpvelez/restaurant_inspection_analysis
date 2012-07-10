import sqlite3

conn = sqlite3.connect('food_inspections.db')
c = conn.cursor()

# Filter out canvass inspections for restaurants still in business
c.execute("CREATE TABLE inspections_clean_restaurants AS SELECT * FROM inspections_clean WHERE facility_type = 'restaurant' AND inspection_type = 'Canvass' AND results != 'Out of Business'")
restaurant_inspections = c.fetchall()

