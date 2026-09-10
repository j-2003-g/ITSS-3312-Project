record2 = "reyes, miguel|M|32|2018-05-17| 3308 DELAFORD STREET |Beat 347|open"
fields = record2.split("|")
name = fields[0].title()
sex = fields[1]
age = int(fields[2])
date = fields[3]
year = int(date[0:4])
addr = fields[4].strip().title()
status = fields[6].upper()
year_unsolved = 2026 - year
summary_record2 = f"CASE: {name} ({sex}, {age}) | {date} | {addr} | " \
                  f"{status} — {year_unsolved} years without an arrest"
print(summary_record2)

record3 = " OKAFOR, SAMUEL J | M | 55 | 2018-07-09 | 1519 westhollow avenue | beat 341 | OPEN "
fields = record3.split(" | ")
name = fields[0].title().strip()
sex = fields[1]
age = int(fields[2])
date = fields[3]
year = int(date[0:4])
addr = fields[4].title()
status = fields[6].upper().strip()
year_unsolved = 2026 - year
summary_record3 = f"CASE: {name} ({sex}, {age}) | {date} | {addr} | " \
                  f"{status} — {year_unsolved} years without an arrest"
print(summary_record3)