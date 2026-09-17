from datetime import date
current_year = date.today().year

# Record 4
record4 = "Nguyen, Daniel | m | 17 | 2018-04-03 | 2846 QUAIL RIDGE ROAD | beat 537 | Open"

fields = record4.strip().split(" | ")

name = fields[0].title() 
sex = fields[1].upper() 
age = int(fields[2]) 
date = fields[3]
year = int(date[0:4]) 
addr = fields[4].title() 
status = fields[6].upper()

years_unsolved = current_year - year

summary = f"CASE: {name} ({sex}, {age}) | {date} | {addr} | {status} — {years_unsolved} years without an arrest"

print(summary)

# Record 5
record5 = "BOOKER, TERRENCE | M | 41 | 2018-11-08 | 907 n. calloway drive | Beat 442 | OPEN"

fields = record5.strip().split(" | ")

name = fields[0].title() 
sex = fields[1].upper() 
age = int(fields[2]) 
date = fields[3]
year = int(date[0:4]) 
addr = fields[4].title() 
status = fields[6].upper()

years_unsolved = current_year - year

summary = f"CASE: {name} ({sex}, {age}) | {date} | {addr} | {status} — {years_unsolved} years without an arrest"

print(summary)
