# ---------- STEP 1: NORMALIZE AND COLLECT ----------

f = open("wk04_data_raw_cases_dupes.txt", "r")    # open the data file

normalized = []                                   # empty list for cleaned records

for line in f:                                    # go through file one line at a time
    clean = line.strip().upper()                  # remove extra spaces and make uppercase
    normalized.append(clean)                      # add cleaned record to the list

f.close()                                         # close the file


# ---------- STEP 2: REMOVE DUPLICATES ----------

unique_records = set(normalized)                   # set keeps only unique records


# ---------- STEP 3: SET UP CONTAINERS ----------

ages = []                                         # list to collect victim ages
per_beat = {}                                     # dictionary: beat -> open case count


# ---------- STEP 4: LOOP THROUGH UNIQUE RECORDS ----------

for rec in unique_records:                        # go through each unique record

    fields = rec.split("|")                       # split record using the | symbol

    age = int(fields[2].strip())                  # get age and convert to integer
    beat = fields[5].strip()                      # get beat
    status = fields[6].strip()                    # get status

    ages.append(age)                              # add age to the ages list

    if status == "OPEN":                          # only count open cases

        if beat in per_beat:                      # if beat is already in dictionary
            per_beat[beat] += 1                   # add 1 to the count
        else:
            per_beat[beat] = 1                    # first open case for this beat


# ---------- STEP 5: CALCULATE AGE AVERAGE ----------

average_age = sum(ages) / len(ages)               # calculate average victim age


# ---------- STEP 6: PRINT REPORT ----------

print("Lines in file:      ", len(normalized))
print("Unique records:     ", len(unique_records))
print("Duplicates removed: ", 60 - len(unique_records))

print("Youngest", min(ages), "/ Oldest", max(ages),
      "/ Average", round(average_age, 1))

print("Beat ranking, most open cases first, with # bars")


# ---------- STEP 7: RANK THE BEATS ----------

for beat in sorted(per_beat,
                   key=per_beat.get,
                   reverse=True):

    count = per_beat[beat]                         # number of open cases for this beat
    bar = "#" * count                              # make one # for each open case

    print(f"Beat {beat:<6}{count:>3}  {bar}")      # print beat, count, and bar 