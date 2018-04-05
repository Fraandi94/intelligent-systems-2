__author__ = "group_3"

import os
import numpy as np
import csv
import sys
from collections import OrderedDict

csv.field_size_limit(sys.maxsize)

def create_and_write_AAM(data_items, output_filename):

    no_artists = len(data_items.keys())
    artist_artist_matrix = np.zeros(shape=(no_artists, no_artists), dtype=np.float32)

    for i, (artist, tokens) in enumerate(data_items.items()):

        sys.stdout.write("\r{0}/{1}".format(i+1, len(data_items)))
        sys.stdout.flush()

        if not tokens:
            continue

        for j, (artist2, tokens2) in enumerate(data_items.items()):
            if j <= i or not tokens2:
               continue

            tokens_length = len(tokens) + len(tokens2)
            tokens_intersection = set(tokens) & set(tokens2)
            similarity = (len(tokens_intersection) / (float(tokens_length) / 2))

            #print similarity, artist, artist2

            artist_artist_matrix[i, j] = similarity
            artist_artist_matrix[j, i] = similarity

    #np.savetxt(output_filename+".txt", artist_artist_matrix, fmt='%0.6f', delimiter='\t', newline='\n')
    np.save(output_filename+".npy", artist_artist_matrix)



if __name__ == '__main__':

    mood_items = OrderedDict()
    with open("./data/C1ku/C1ku_artists_moods.csv", 'r') as f:
        reader = csv.DictReader(f, delimiter='\t', quoting=csv.QUOTE_NONE)
        for row in reader:
            if row["moods"]:
                mood_items[row["id"]] = row["moods"].split(",")
            else:
                mood_items[row["id"]] = []

    create_and_write_AAM(mood_items, "./data/C1ku/C1ku_AAM_moods")


    wikilinks_items = OrderedDict()
    with open("./data/C1ku/C1ku_artists_wikilinks.csv", 'r') as f:
        reader = csv.DictReader(f, delimiter='\t', quoting=csv.QUOTE_NONE)
        for row in reader:
            if row["links"]:
                wikilinks_items[row["id"]] = row["links"].split(",")
            else:
                wikilinks_items[row["id"]] = []

    create_and_write_AAM(wikilinks_items, "./data/C1ku/C1ku_AAM_wikilinks")
