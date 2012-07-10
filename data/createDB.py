import csv
import sqlite3
from AsciiDammit import asciiDammit
import datetime

def mode(l) :
  counts = [(l.count(val), val) for val in set(l) if val != '']
  return sorted(counts)[-1][1]

conn = sqlite3.connect('food_inspections.db')
c = conn.cursor()

c.execute('''DROP TABLE IF EXISTS inspections_raw''')
c.execute('''DROP TABLE IF EXISTS inspections_clean''')

c.execute('''CREATE TABLE inspections_raw
             (inspection_id int, dba text, aka text, license_no int,
              facility_type text, risk text, address text, city text,
              state text, zip text, inspection_date text,
              inspection_type text, results int,
              violations text, x_coord real, y_coord real, lat real,
              long real, location text)''')
c.execute('''CREATE TABLE inspections_clean
             (inspection_id int, dba text, aka text, license_no int,
              facility_type text, risk text, address text, 
              zip text, inspection_date date, inspection_type text,
              results int, violations text, lat real, long real)''')


conn.commit()



with open('food_inspections.csv', 'rb') as f :
  reader = csv.reader(f)
  reader.next()
  for row in reader:
    values = [asciiDammit(field) for field in row]
    c.execute('''INSERT INTO inspections_raw VALUES
    (?, ?, ?, ?,
     ?, ?, ?, ?,
     ?, ?, ?, ?,
     ?, ?, ?, ?,
     ?, ?, ?)''', values)
    

conn.commit()

fields = ('inspection_id', 'dba', 'aka', 'license_no',
          'facility_type', 'risk', 'address', 'zip',
          'inspection_date', 'inspection_type', 'results',
          'violations', 'lat', 'long')

c.execute('''SELECT %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s from inspections_raw ORDER BY license_no''' % fields)
subset = c.fetchall()

# Schools and Restaurants mixed up together

problem_licenses = [22992, 1578, 29151, 25152, 26651, 22951, 23431,
                    22971, 23891, 23031, 1362, 26821, 25251, 25811,
                    23081, 31231, 18236, 26591, 31061, 1516266,
                    2031937, 2041759, 1816680, 24621, 70217, 22641,
                    22952, 22181, 23021, 23011, 46041, 23051, 22811,
                    46041, 26791, 25901, 51011, 46241, 23101, 23041,
                    22361, 2142655, 1932, 24871, 23071, 26891, 29151,
                    23151, 0]

for row in subset :
  values = []
  skip = False
  for i, field in enumerate(fields):
    if field == "license_no" :
      license_no = row[i]
      if license_no in problem_licenses :
        skip = True
        break
       
    if field == "inspection_date" :
      values.append(datetime.datetime.strptime(row[i], "%m/%d/%Y"))
    elif field == "facility_type" :
      c.execute('''SELECT facility_type FROM inspections_raw WHERE license_no = ?''', (license_no,))

      facility_types = c.fetchall()
      facility_types = [fac_type[0].lower().strip() for fac_type in facility_types]
      if len(set(facility_types)) > 1 :
        print (row[1], row[3], row[4]) 
        values.append(mode(facility_types))
      else :
        values.append(facility_types[0])
    else :
      values.append(row[i])
  if skip != True :
    c.execute('''INSERT INTO inspections_clean VALUES
    (?, ?, ?, ?,
    ?, ?, ?, ?,
    ?, ?, ?, ?,
    ?, ?)''', values)


conn.commit()
c.close()
