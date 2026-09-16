record = "CARTER, DEMARCUS | m | 36 | 2018-03-22 | 412 larkmoor lane | beat 352 | OPEN"

fields = record.strip().split(" | ")
name = fields[0].title()
sex = fields[1].upper()
age = int(fields[2]) 
date = fields[3]
year = int(date[0:4]) 
addr = fields[4].title()
status = fields[6]

years_unsolved = 2026 - year

print(f"{'CASE':<20}{'AGE':>6}{'YEARS UNSOLVED':>18}")

case_str = f"{name} ({sex})"
print(f"{case_str:<20}{age:>6}{years_unsolved:>18}")