__author__ = "group_3"

import numpy as np
import json
import csv
from collections import OrderedDict

UAM_FILE = "./data/C1ku/C1ku_UAM.txt"

def create_UAM():

    UAM = np.loadtxt(UAM_FILE, delimiter='\t', dtype=np.float32)

    # Get sum of play events per user and per artist
    sum_pc_user = np.sum(UAM, axis=1)
    sum_pc_artist = np.sum(UAM, axis=0)

    # Normalize UAM
    no_users = UAM.shape[0]
    no_artists = UAM.shape[1]

    # np.tile: take sum_pc_user no_artists times (results in an array of length no_artists*no_users)
    # np.reshape: reshape the array to a matrix
    # np.transpose: transpose the reshaped matrix
    artist_sum_copy = np.tile(sum_pc_user, no_artists).reshape(no_artists, no_users).transpose()

    # Perform sum-to-1 normalization
    UAM = UAM / artist_sum_copy

    # Inform user
    print "UAM created. Users: " + str(UAM.shape[0]) + ", Artists: " + str(UAM.shape[1])


    # Write UAM
    np.savetxt("data/C1ku/C1ku_UAM_normalized.txt", UAM, fmt="%0.6f", delimiter="\t", newline="\n")
    np.save("data/C1ku/C1ku_UAM_normalized.npy", UAM)


if __name__ == '__main__':

    create_UAM()

