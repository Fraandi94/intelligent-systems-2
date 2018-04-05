__author__ = "group_3"


import json
import time
import csv
from LastFM_helper import LastFM
from collections import OrderedDict
import geopy
import pycountry


LASTFM_API_KEY = "4cb074e4b8ec4ee9ad3eb37d6f7eb240"


LastFM = LastFM(LASTFM_API_KEY)
geolocator = geopy.Bing(api_key= "AotMTOJdAL1wUlTz42m98rueSVssyIPKQwX8BSUbS_q8xByKrkblVGGoKgVs_USp")

USERS_FILE = "./data/C1ku/C1ku_idx_users.txt"
ALL_USERS_FILE = "./data/C1ku/LFM1b_users.txt"


def read_from_file(filename):
    data = []
    with open(filename, 'r') as f:
        reader = csv.reader(f, delimiter='\t', quoting=csv.QUOTE_NONE)
        for row in reader:
            data.append(row[0])
    return data

all_users = {}

with open(ALL_USERS_FILE, 'r') as f:
    reader = csv.reader(f, delimiter='\t', quoting=csv.QUOTE_NONE)
    for row in reader:
        all_users[row[0]] = {"age": row[3], "username": row[1], "country": row[2], "gender": row[4]}

users_extended = OrderedDict()
users = read_from_file(USERS_FILE)

countries = {}
country_codes = {}

def fetch_country_codes():
    for country in pycountry.countries:
        country_codes[country.name] = country.alpha2

fetch_country_codes()

for user in users:

    current = LastFM.request('user.getInfo', {"user": all_users[user]["username"]})
    #print json.dumps(current)
    current = current.get("user", None)
    if not current:
        print "ERROR!"
        users_extended[user] = all_users[user]
        users_extended[user]["usertype"] = ""
        users_extended[user]["longitude"] = ""
        users_extended[user]["latitude"] = ""
        continue

    playcount = int(current.get("playcount"))
    registered = int(current.get("registered").get("unixtime"))

    register_days = int((time.time() - registered) / 3600 / 24)
    LE_per_day = float(playcount) / float(register_days)

    # Check in which playcount range a friend is
    if LE_per_day < 5:
        usertype = "rare"
    elif LE_per_day < 30:
        usertype = "average"
    elif LE_per_day < 60:
        usertype = "many"
    elif LE_per_day >= 60:
        usertype = "power"

    users_extended[user] = all_users[user]
    users_extended[user]["usertype"] = usertype

    country = all_users[user]["country"]

    country_name = ""

    if not country:

        country_name = current.get("country", None)

        if not country_name:
            #print "ERROR!"
            users_extended[user]["longitude"] = ""
            users_extended[user]["latitude"] = ""
            continue

        country_code = country_codes.get(country_name, 'Unknown code')

        users_extended[user]["country"] = country_code

        print country_code, " : ", country_name

    else:

        #print "in else"

        if country == "UK":
            country = "GB"

        country_name = pycountry.countries.get(alpha2=country).name

    if not countries.get(country_name):
        geo = geolocator.geocode(country_name)
        countries[country_name] = geo
    else:
        geo = countries.get(country_name)

    #print "extended", json.dumps(users_extended[user])

    if(country == "KR"):
        users_extended[user]["longitude"] = 127.024612
        users_extended[user]["latitude"] = 37.532600

    elif(country == "IR"):
        users_extended[user]["longitude"] = 51.404343
        users_extended[user]["latitude"] = 35.715298

    else:
        print geo
        users_extended[user]["longitude"] = geo.longitude or ""
        users_extended[user]["latitude"] = geo.latitude or ""

    print json.dumps(users_extended[user])
print json.dumps(users_extended)




with open("data/C1ku_users_extended.csv", "w") as f:
   f.write("user" + "\t" + "age" + "\t" + "country" + "\t" + "long" + "\t" + "lat" + "\t" + "gender" + "\t" + "usertype" + "\n")
   for user in users_extended:
       f.write(users_extended[user]["username"].encode('utf-8') + "\t" + str(users_extended[user]["age"]) + "\t" + users_extended[user]["country"].encode('utf-8') + "\t" + str(users_extended[user]["longitude"]) + "\t" + str(users_extended[user]["latitude"]) + "\t" + users_extended[user]["gender"].encode('utf-8') + "\t" + users_extended[user]["usertype"].encode('utf-8') + "\n")