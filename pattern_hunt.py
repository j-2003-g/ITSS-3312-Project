import re                                              # import regular expression module


# ---------- STEP 1: CREATE EXTRACTOR FUNCTIONS ----------

def extract_phones(text):                              # function to find phone numbers
    """Find phone numbers in a tip."""                  # explain what the function does
    return re.findall(
        r"\(?\d{3}\)?[ -]\d{3}-\d{4}", text)           # return all matching phone numbers


def extract_case_refs(text):                           # function to find case references
    """Find case references in a tip."""                # explain what the function does
    return re.findall(r"CC-\d{5}", text)                # return case refs like CC-12345


def extract_beats(text):                               # function to find beat numbers
    """Find beat numbers in a tip."""                   # explain what the function does
    return re.findall(r"[Bb]eat (\d{3})", text)         # return 3-digit beat numbers


def extract_iso_dates(text):                           # function to find ISO dates
    """Find ISO dates in a tip."""                      # explain what the function does
    return re.findall(r"\d{4}-\d{2}-\d{2}", text)       # return dates like 2019-02-19


def extract_us_dates(text):                            # function to find US numeric dates
    """Find US numeric dates in a tip."""               # explain what the function does
    return re.findall(
        r"\d{1,2}/\d{1,2}/\d{4}", text)                # return dates like 4/7/2019



# ---------- STEP 2: SUMMARIZE ONE TIP ----------

def summarize_tip(tip):                                # function to summarize one tip
    """Extract patterns from one tip."""                # explain what the function does

    phones = extract_phones(tip)                        # get phone numbers from the tip
    refs = extract_case_refs(tip)                       # get case references from the tip
    beats = extract_beats(tip)                          # get beat numbers from the tip
    iso_dates = extract_iso_dates(tip)                  # get ISO dates from the tip
    us_dates = extract_us_dates(tip)                    # get US numeric dates from the tip

    return phones, refs, beats, iso_dates, us_dates     # return all extracted information



# ---------- STEP 3: READ AND COLLECT TIPS ----------

f = open("wk05_data_tipline.txt", "r")                  # open the tip-line data file

tips = []                                               # empty list to collect tips

for line in f:                                          # go through file one line at a time
    tips.append(line.strip())                            # clean and add tip to the list

f.close()                                               # close the file



# ---------- STEP 4: SET UP CALLBACK COUNTERS ----------

with_callback = 0                                       # count tips with a phone number
no_callback = 0                                         # count tips without a phone number



# ---------- STEP 5: PROCESS AND PRINT EACH TIP ----------

for i, tip in enumerate(tips, start=1):                 # go through tips and number from 1

    phones, refs, beats, iso_dates, us_dates = summarize_tip(tip)
                                                        # get information from this tip

    print(f"TIP {i}: phone={phones} case={refs} beat={beats} "
          f"iso_date={iso_dates} us_date={us_dates}")   # print summary for this tip

    if len(phones) >= 1:                                # check if tip has a phone number
        with_callback = with_callback + 1               # add 1 to callback count
    else:                                               # if there is no phone number
        no_callback = no_callback + 1                   # add 1 to no-callback count



# ---------- STEP 6: PRINT FINAL RESULTS ----------

print()                                                 # print an empty line
print("Tips processed:", len(tips))                     # print total number of tips
print("Tips with a callback:", with_callback)           # print tips with phone numbers
print("Tips with NO callback:", no_callback)             # print tips without phone numbers