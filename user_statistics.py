__author__ = "group_3"

import json
import csv
from collections import OrderedDict
import pycountry

EXTENDED_USERS_FILE = "./data/C1ku/C1ku_users_extended.csv"

users = OrderedDict()
with open(EXTENDED_USERS_FILE, "r") as f:
    reader = csv.DictReader(f, delimiter='\t', quoting=csv.QUOTE_NONE)
    for row in reader:
        users[row["user"]] = { "gender": row["gender"], "usertype": row["usertype"], "country": row["country"], "age": row["age"] }


countries = {}
ages = {"young": 0, "junior": 0, "middle": 0, "senior": 0, "old": 0, "unknown": 0}
genders = {"m": 0, "f": 0, "n": 0}
usertypes = {"rare": 0, "average": 0, "many": 0, "power": 0}

for user in users:

    country = users[user].get("country")
    gender = users[user].get("gender")
    current_age = int(users[user].get("age"))
    usertype = users[user].get("usertype")

    if current_age >= 0 and current_age < 18:
        age = "young"
    elif current_age >= 18 and current_age < 25:
        age = "junior"
    elif current_age >= 25 and current_age < 40:
        age = "middle"
    elif current_age >= 40 and current_age < 60:
        age = "senior"
    elif current_age >= 60 and current_age < 120:
        age = "old"
    else:
        age = "unknown"

    ages[age] += 1

    if country:
        if country == "UK":
            country = "GB"
        country_name = pycountry.countries.get(alpha2=country).name
        countries[country_name] = countries.get(country_name, 0) + 1
    else:
        countries["unknown"] = countries.get("unknown", 0) + 1

    if usertype:
        usertypes[usertype] += 1
    else:
        usertypes["unknown"] = usertypes.get("unknown", 0) + 1

    if gender:
        genders[gender] += 1
    else:
        genders["unknown"] = genders.get("unknown", 0) + 1



print "Ages: " + json.dumps(ages)
print "Genders: " + json.dumps(genders)
print "Countries: " + json.dumps(countries)
print "User Categories: " + json.dumps(usertypes)