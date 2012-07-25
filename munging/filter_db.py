import sqlite3

conn = sqlite3.connect('../data/food_inspections.db')
c = conn.cursor()

c.execute("DROP TABLE IF EXISTS inspections_clean_restaurants")
c.execute("DROP TABLE IF EXISTS inspections_clean_restaurants_recent")

# Filter out canvass inspections for restaurants still in business
c.execute('''CREATE TABLE inspections_clean_restaurants AS SELECT * FROM inspections_clean 
          WHERE facility_type = "restaurant" AND inspection_type = "Canvass" AND results != "Out of Business"''')

c.execute('''CREATE TABLE inspections_clean_restaurants_recent AS SELECT inspection_id, dba, aka, license_no, 
          facility_type, risk, address, zip, MAX(inspection_date), inspection_type, results, violations, lat, long
          FROM inspections_clean_restaurants GROUP BY license_no''')

conn.close()

