__author__ = "group_3"

import os
import numpy as np
import csv
import sys
import geopy.distance as gdistance
from collections import OrderedDict

csv.field_size_limit(sys.maxsize)

def create_and_write_UUM(users, output_filename):

    no_users = len(users.keys())
    user_user_matrix = np.zeros(shape=(no_users, no_users), dtype=np.float32)
    #user_user_matrix_age = np.zeros(shape=(no_users, no_users), dtype=np.float32)
    #user_user_matrix_gender = np.zeros(shape=(no_users, no_users), dtype=np.float32)
    #user_user_matrix_usertype = np.zeros(shape=(no_users, no_users), dtype=np.float32)
    #user_user_matrix_distance = np.zeros(shape=(no_users, no_users), dtype=np.float32)
    #user_user_matrix_country = np.zeros(shape=(no_users, no_users), dtype=np.float32)


    for i, (user, items) in enumerate(users.items()):

        sys.stdout.write("\r{0}/{1}".format(i+1, no_users))
        sys.stdout.flush()

        if not items:
            continue

        for j, (user2, items2) in enumerate(users.items()):
            if j <= i or not items2:
                continue

            # age
            age_difference_abs = abs(float(items["age"]) - float(items2["age"]))

            if items["age"] == "-1" or items2["age"] == "-1":
                age_similarity = 0

            else:
                if age_difference_abs == 0:
                    age_similarity = 1
                elif age_difference_abs > 1 and age_difference_abs <= 2:
                    age_similarity = 0.80
                elif age_difference_abs > 2 and age_difference_abs <= 5:
                    age_similarity = 0.60
                elif age_difference_abs > 5 and age_difference_abs <= 9:
                    age_similarity = 0.40
                elif age_difference_abs > 9 and age_difference_abs <= 15:
                    age_similarity = 0.20
                else:
                    age_similarity = 0

            # gender
            if items["gender"] == items2["gender"] and items["gender"] != "n":
                gender_similarity = 1
            else:
                gender_similarity = 0

            #   country
            if items["latitude"] and items2["latitude"]:
                items_koordinates = (items["latitude"], items["longitude"])
                items2_koordinates = (items2["latitude"], items2["longitude"])

                distance = gdistance.great_circle(items_koordinates, items2_koordinates).meters / 1000

                if distance == 0:
                    distance_similarity = 1
                elif distance > 0 and distance <= 500:
                    distance_similarity = 0.9
                elif distance > 500 and distance <= 750:
                    distance_similarity = 0.8
                elif distance > 750 and distance <= 1000:
                    distance_similarity = 0.7
                elif distance > 1000 and distance <= 1500:
                    distance_similarity = 0.6
                elif distance > 1500 and distance <= 2000:
                    distance_similarity = 0.5
                elif distance > 2000 and distance <= 2500:
                    distance_similarity = 0.4
                elif distance > 2500 and distance <= 3000:
                    distance_similarity = 0.3
                elif distance > 3000 and distance <= 3500:
                    distance_similarity = 0.2
                elif distance > 3500 and distance <= 4000:
                    distance_similarity = 0.1
                else:
                    distance_similarity = 0

            else:
                distance_similarity = 0

            # usertype
            if items["usertype"] == items2["usertype"]:
                usertype_similarity = 1
            else:
                usertype_similarity = 0


            similarity = (age_similarity + gender_similarity + distance_similarity + usertype_similarity)/4
            #print "sim: " , similarity
            user_user_matrix[i, j] = similarity
            user_user_matrix[j, i] = similarity

    np.savetxt(output_filename + ".txt", user_user_matrix, fmt='%0.6f', delimiter='\t', newline='\n')


if __name__ == '__main__':

    users = OrderedDict()
    with open("./data/C1ku/C1ku_users_extended.csv", 'r') as f:
        reader = csv.DictReader(f, delimiter='\t', quoting=csv.QUOTE_NONE)
        for row in reader:
            users[row["user"]] = { "longitude": row["long"], "latitude": row["lat"], "gender": row["gender"], "usertype": row["usertype"], "country": row["country"], "age": row["age"] }

    create_and_write_UUM(users, "./data/C1ku/C1ku_UUM")


