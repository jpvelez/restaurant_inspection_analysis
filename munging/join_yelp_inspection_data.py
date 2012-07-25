import csv
import json
import sqlite3

# Fetch inspection data used to generate yelp data through api
conn = sqlite3.connect('../data/food_inspections.db')
c = conn.cursor()

c.execute('SELECT * FROM inspections_clean_restaurants_recent_normalized_randomized LIMIT 900') 
recent_inspections = c.fetchall()

# Map inspection id to inspection values. This map will be used to add additional inspection data to yelp data down below, which already includes inspection id, name, and address.
insp_id_to_values = {}

for insp in recent_inspections:
    insp_id = insp[0]

    insp_values = {}
    insp_values['risk'] = insp[5]
    insp_values['last_inspection_date'] = insp[8]
    insp_values['results'] = insp[10]
    insp_values['lat'] = insp[12]
    insp_values['long'] = insp[13]

    insp_id_to_values[insp_id] = insp_values

# Fetch yelp data
yelp_restaurant_responses = open('../data/yelp_restaurants_0-900.json')
 
# Data merging step. Iterate through yelp data, extracting yelp, basic inspection, and additional inspection values, and adding these values to a list.
result_list = []

missing_biz = 0
missing_cat = 0

for row in yelp_restaurant_responses:

    response = json.loads(row)   # Convert json-formatted string to dict

    # Get basic inspection values from yelp data
    inspection_values_yelp = response['inspection_restaurant']
    
    # Get additional inspection values from insp_id_to_values map
    insp_id = response['inspection_restaurant']['inspection_id']
    inspection_values_map = insp_id_to_values[insp_id] 

    # Get yelp data, when yelp categories or businesses list missing, print restaurant and add to counter
    yelp_values = {}
    try:
        yelp_values['yelp_rating'] = response['businesses'][0]['rating']
        yelp_values['yelp_id'] = response['businesses'][0]['id']
        yelp_values['yelp_is_closed'] = response['businesses'][0]['is_closed'] # KEEP ADDING VALUES, THEN MERGE ALL THE VALUE DICTS AND ADD TO RESULT, THEN ANNOTATE EVERYTHING
        yelp_values['yelp_address'] = response['businesses'][0]['location']['address'][0]
        yelp_values['yelp_name'] = response['businesses'][0]['name']
        # yelp_values['yelp_phone'] = response['businesses'][0]['phone']
        yelp_values['yelp_review_count'] = response['businesses'][0]['review_count']

        try:
            yelp_values['yelp_category'] = response['businesses'][0]['categories'][0][0]
        except KeyError:
            print "Inspection restaurant %s has no yelp category, adding NULL value." % inspection_values_yelp['name']
            yelp_values['yelp_category'] = 'NULL'
            missing_cat += 1

        # Merge the three sets of values
        unicode_result = dict(inspection_values_yelp, **inspection_values_map)
        unicode_result.update(yelp_values)   

        # Convert unicode keys and values to byte str so python doesn't bitch when writing data to file
        result = {}
        for k, v in unicode_result.items():
            if isinstance(k, unicode) == True:
                k = k.encode('utf8', 'replace')
            if isinstance(v, unicode) == True:
                v = v.encode('utf8', 'replace')
            result[k] = v

        # Add merged data to result list
        result_list.append(result)   
        print "Adding to result_list:", result

    except (IndexError, KeyError):
        print "Inspection restaurant %s fetched no yelp businesses." % inspection_values_yelp['name']
        missing_biz += 1
 
# # Save merged yelp + inspection data to new db table
# c.execute("DROP TABLE IF EXISTS restaurants_yelp_inspection_nomatch")
# c.execute('''CREATE TABLE restaurants_yelp_inspection_nomatch
#             (inspection_id int, inspection_aka_name text, inspection_address text,
#             inspection_results text, last_inspection_date date, inspection_risk text,
#             inspection_lat real, inspection_long real, yelp_id int, yelp_name text,
#             yelp_address text, yelp_rating int, yelp_is_closed text, 
#             yelp_review_count int, yelp_category text)''')
# 
# print "Creating restaurants_yelp_inspection_nomatch table in food_inspection.db"
# 
# for result in result_list:
#     sql = u'''INSERT INTO restaurants_yelp_inspection_nomatch VALUES
#     (%(inspection_id)s, %(name)s, %(address)s, 
#     %(results)s, %(last_inspection_date)s, %(risk)s,
#     %(lat)s, %(long)s, %(yelp_id)s, %(yelp_name)s,
#     %(yelp_address)s, %(yelp_rating)s, %(yelp_is_closed)s, 
#     %(yelp_review_count)s, %(yelp_category)s)''' % result
# 
#     print 'Adding to db:', result
# 
#     c.execute(sql)
# 
# conn.commit()
# 
# Save merged yelp + inspection data to csv

output_file = open('data.csv', 'w+') 
fieldnames = ('inspection_id', 'name', 'address', 'results', 'last_inspection_date', 'risk', 'lat', 'long', 'yelp_id', 'yelp_name', 'yelp_address', 'yelp_rating', 'yelp_is_closed', 'yelp_review_count', 'yelp_category') 

writer = csv.DictWriter(output_file, fieldnames)
writer.writeheader()

csv_counter = 0
for result in result_list:

    writer.writerow(result)

    print 'Writing to csv:', result
    csv_counter +=1


print "This many rows in db:", len(recent_inspections)
print "%s restaurants had no yelp businesses." % missing_biz
print "%s restaurants had no yelp categories." % missing_cat
print "This many merged rows created:", len(result_list)
print "This many row written to csv:", csv_counter
