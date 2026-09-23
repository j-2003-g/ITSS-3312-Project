DATA_FILE = "wk03_data_raw_cases_50.txt" # states our data file
CURRENT_YEAR = 2026 # states our current year is 2026
STALE_YEARS = 5  # states that a case is considered stale if it has been open for 5 or more years

file = open(DATA_FILE) # open the data file for reading
records = file.readlines() # read all the lines from the file into a list
file.close() # close the file after reading

total_records = 0 # initialize a counter for the total number of records
open_count = 0 # initialize a counter for the number of open cases
stale_count = 0 # initialize a counter for the number of stale cases
juvenile_open_count = 0 # initialize a counter for the number of open juvenile cases
oldest_year = CURRENT_YEAR # initialize a variable to track the oldest year of an open case, initialize to current year initially to ensure any year found will be earlier than this
oldest_name = "" # initialize a variable to track the name of the oldest open case

for line in records: # iterate through each line in the records list to process the data in each line
    line = line.strip() # remove leading and trailing whitespace from the line
    if line == "": # check if the line is empty. If empty, skip to the next iteration of the loop
        continue  # skip blanks, keep looping

    fields = line.split("|") # split the line into fields using the pipe character as a delimiter
    if len(fields) != 7: # check if the line has the expected number of fields (name, sex, age, case date, address, patrol area number, case status)
        continue  # skip lines that don't have the expected number of fields

    name = fields[0].strip().title() # extract the name field, remove leading/trailing whitespace, and convert to Title Case
    age = int(fields[2].strip()) # extract the age field, remove leading/trailing whitespace, and convert to an integer
    year = int(fields[3].strip()[0:4]) # extract the case year from case date field, remove leading/trailing whitespace, and convert to an integer
    status = fields[6].strip().upper() # extract the status field, remove leading/trailing whitespace, and convert to UPPERCASE

    total_records += 1 # increment the total records counter for each valid record processed
    years_unsolved = CURRENT_YEAR - year # calculate the number of years the case has been unsolved by subtracting the case year from the current year

    print(f"{name}: {years_unsolved} years unsolved") # print the name of the case and the number of years it has been unsolved (f-strings let you plug in variables into the string)

    if years_unsolved >= STALE_YEARS: # check if the case has been unsolved for 5 or more years 
        flag = "*** STALE ***" # if the case is stale, set the flag to indicate it is stale
    elif years_unsolved >= 2: # check if the case has been unsolved for 2 or more years but less than 5 years
        flag = "aging" # if the case is aging, set the flag to indicate it is aging
    else: # if the case has been unsolved for less than 2 years
        flag = "recent" # if the case is recent, set the flag to indicate it is recent

    if status == "OPEN" and years_unsolved >= STALE_YEARS: # check if the case is open and has been unsolved for 5 or more years (aka it is a stale case)
        print(f"{name} {flag}") # print the name of the case and the flag indicating it is stale

    if status == "OPEN": # check if the case is open
        open_count += 1 # increment the open cases counter

        if years_unsolved >= STALE_YEARS: # check if the case has been unsolved for 5 or more years (aka it is a stale case)
            stale_count += 1 # increment the stale cases counter

        if age < 18: # check if the case is a juvenile case (victim age less than 18)
            juvenile_open_count += 1 # increment the juvenile open cases counter

        if year < oldest_year: # check if the case year is earlier than the current oldest year found
            oldest_year = year # update the oldest year to the current case year if it is earlier than the previously recorded oldest year
            oldest_name = name # update the oldest name to the current case name if it is earlier than the previously recorded oldest year

print() # print a blank line for better readability in the output to separate case data processing and report summary
print(f"Total records: {total_records}") # print the total number of valid records processed
print(f"Open cases: {open_count}") # print the number of open cases
print(f"Stale (>= {STALE_YEARS} yrs): {stale_count}") # print the number of stale cases
print(f"Juvenile open cases: {juvenile_open_count}") # print the number of juvenile open cases
print(f"Oldest open case: {oldest_name} ({oldest_year})") # print the name and year of the oldest open case