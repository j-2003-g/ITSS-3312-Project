from datetime import date

current_year = date.today().year

# Record 1
record1 = "CARTER, DEMARCUS | m | 36 | 2018-03-22 | 412 larkmoor lane | beat 352 | OPEN"

fields = record1.strip().split(" | ")

name = fields[0].title()
sex = fields[1].upper()
age = int(fields[2])
date_str = fields[3]
year = int(date_str[0:4])
addr = fields[4].title()
status = fields[6].upper()

years_unsolved = current_year - year

print(f"{'CASE':<20}{'AGE':>6}{'YEARS UNSOLVED':>18}")

case_str = f"{name} ({sex})"
print(f"{case_str:<20}{age:>6}{years_unsolved:>18}")

# Record 2
record2 = "reyes, miguel|M|32|2018-05-17| 3308 DELAFORD STREET |Beat 347|open"

fields = [f.strip() for f in record2.strip().split("|")]

name = fields[0].title()
sex = fields[1].upper()
age = int(fields[2])
date_str = fields[3]
year = int(date_str[0:4])
addr = fields[4].title()
status = fields[6].upper()

years_unsolved = current_year - year

case_str = f"{name} ({sex})"
print(f"{case_str:<20}{age:>6}{years_unsolved:>18}")

# Record 3
record3 = " OKAFOR, SAMUEL J | M | 55 | 2018-07-09 | 1519 westhollow avenue | beat 341 | OPEN "

fields = record3.strip().split(" | ")

name = fields[0].title()
sex = fields[1].upper()
age = int(fields[2])
date_str = fields[3]
year = int(date_str[0:4])
addr = fields[4].title()
status = fields[6].upper()

years_unsolved = current_year - year

case_str = f"{name} ({sex})"
print(f"{case_str:<20}{age:>6}{years_unsolved:>18}")

# Record 4
record4 = "Nguyen, Daniel | m | 17 | 2018-04-03 | 2846 QUAIL RIDGE ROAD | beat 537 | Open"

fields = record4.strip().split(" | ")

name = fields[0].title()
sex = fields[1].upper()
age = int(fields[2])
date_str = fields[3]
year = int(date_str[0:4])
addr = fields[4].title()
status = fields[6].upper()

years_unsolved = current_year - year

case_str = f"{name} ({sex})"
print(f"{case_str:<20}{age:>6}{years_unsolved:>18}")

# Record 5
record5 = "BOOKER, TERRENCE | M | 41 | 2018-11-08 | 907 n. calloway drive | Beat 442 | OPEN"

fields = record5.strip().split(" | ")

name = fields[0].title()
sex = fields[1].upper()
age = int(fields[2])
date_str = fields[3]
year = int(date_str[0:4])
addr = fields[4].title()
status = fields[6].upper()

years_unsolved = current_year - year

case_str = f"{name} ({sex})"
print(f"{case_str:<20}{age:>6}{years_unsolved:>18}")