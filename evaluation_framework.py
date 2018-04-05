__author__ = 'group_3'

import csv
import numpy as np
from sklearn import cross_validation
import random
import sys

import recommender


NUMBER_OF_FOLDS = 10
VERBOSE = False


ARTISTS_FILE = "./data/C1ku/C1ku_idx_artists.txt"
USERS_FILE = "./data/C1ku/C1ku_idx_users.txt"
UAM_FILE = "./data/C1ku/C1ku_UAM_normalized.txt"
UUM_FILE = "./data/C1ku/C1ku_UUM.txt"
AAM_FILE_WIKI = "./data/C1ku/C1ku_AAM_wikilinks.npy"
AAM_FILE_MOODS = "./data/C1ku/C1ku_AAM_moods.npy"


def read_from_file(filename):
    data = []
    with open(filename, 'r') as f:
        reader = csv.reader(f, delimiter='\t', quoting=csv.QUOTE_NONE)
        headers = reader.next()
        for row in reader:
            data.append(row[0])
    return data


def copy_UAM_and_remove_artists(UAM, u, artist_indexes_test):
    copy_UAM = UAM.copy()       # we need to create a copy of the UAM, otherwise modifications within recommend function will effect the variable
    # Remove information on test artists from seed's listening vector
    # by setting listening events of seed user to 0
    copy_UAM[u, artist_indexes_test] = 0.0
    # Seed user normalization (sum-to-1)
    copy_UAM[u, :] = copy_UAM[u, :] / np.sum(copy_UAM[u, :])
    return copy_UAM


def run(type="RB_A", no_of_users=9999999):
    avg_precision = 0;
    avg_recall = 0;

    no_users = min(no_of_users, UAM.shape[0])
    no_artists = UAM.shape[1]

    user_count = 0
    for u in range(0, no_users):

        # Get seed user's artists listened to
        user_artists_idx = np.nonzero(UAM[u, :])[0]
        if len(user_artists_idx) < NUMBER_OF_FOLDS:
            continue
        user_count += 1

        if not VERBOSE:
            sys.stderr.write("\r{0}:\t{1}/{2}".format(type, u+1, no_users))
            sys.stderr.flush()

        # Split user's artists into train and test set for cross-fold (CV) validation
        fold = 0
        kf = cross_validation.KFold(len(user_artists_idx), n_folds=NUMBER_OF_FOLDS)  # create folds (splits) for 5-fold CV
        for train_artists_idx, test_artists_idx in kf:  # for all folds

            # Show progress
            if VERBOSE:
                print "User: " + str(u) + ", Fold: " + str(fold) + ", Training items: " + str(len(train_artists_idx)) + ", Test items: " + str(len(test_artists_idx)),      # the comma at the end avoids line break

            # Run recommendation method specified in type
            # NB: user_artists_idx[train_artists_idx] gives the indices of training artists
            #K_RB = 10          # for RB: number of randomly selected artists to recommend
            #K_CB = 3           # for CB: number of nearest neighbors to consider for each artist in seed user's training set
            #K_CF = 3           # for CF: number of nearest neighbors to consider for each user
            #K_HR = 10          # for hybrid: number of artists to recommend at most


            if type == "RB_A":          # random baseline for random artist
                dict_recommended_artists_idx = recommender.random_baseline_artist(np.setdiff1d(range(0, no_artists), user_artists_idx[train_artists_idx]), K_RB)

            elif type == "RB_U":          # random baseline for random user
                dict_recommended_artists_idx = recommender.random_baseline_user(u, np.setdiff1d(UAM[u, :], user_artists_idx[train_artists_idx]), copy_UAM, K_RB)

            elif type == "PB":        # popularity based
                copy_UAM = copy_UAM_and_remove_artists(UAM, u, user_artists_idx[test_artists_idx])
                dict_recommended_artists_idx = recommender.popularity_based(copy_UAM, K_PB)

            elif type == "CF":        # collaborative filtering
                copy_UAM = copy_UAM_and_remove_artists(UAM, u, user_artists_idx[test_artists_idx])
                dict_recommended_artists_idx = recommender.collaborative_filtering(copy_UAM, u, user_artists_idx[train_artists_idx], K_CF, KNN_CF)

            elif type == "CF_UUM":        # collaborative filtering for UUM
                copy_UAM = copy_UAM_and_remove_artists(UAM, u, user_artists_idx[test_artists_idx])
                dict_recommended_artists_idx = recommender.collaborative_filtering(copy_UAM, u, user_artists_idx[train_artists_idx], K_CF, KNN_CF, UUM=UUM)

            elif type == "CB_WIKI":        # content-based recommender for our wikipedia-links
                dict_recommended_artists_idx = recommender.content_based(AAM_WIKI, user_artists_idx[train_artists_idx], KNN_CB, K_CB)

            elif type == "CB_MOODS":        # content-based recommender for our moods
                dict_recommended_artists_idx = recommender.content_based(AAM_MOODS, user_artists_idx[train_artists_idx], KNN_CB, K_CB)

            elif type == "HR_CB_WIKI_CB_MOODS":     # hybrid of CB_WIKI and CB_MOODS
                dict_recommended_artists_idx = recommender.hybrid([
                    recommender.content_based(AAM_WIKI, user_artists_idx[train_artists_idx], KNN_CB, K_CB),
                    recommender.content_based(AAM_MOODS, user_artists_idx[train_artists_idx], KNN_CB, K_CB)
                ], no_artists, K_HR)

            elif type == "HR_CF_CB_WIKI":     # hybrid of CF and CB_WIKI
                copy_UAM = copy_UAM_and_remove_artists(UAM, u, user_artists_idx[test_artists_idx])
                dict_recommended_artists_idx = recommender.hybrid([
                    recommender.content_based(AAM_WIKI, user_artists_idx[train_artists_idx], KNN_CB, K_CB),
                    recommender.collaborative_filtering(copy_UAM, u, user_artists_idx[train_artists_idx], K_CF, KNN_CF)
                ], no_artists, K_HR)

            elif type == "HR_CF_CB_WIKI_weighted":     # hybrid of CF and CB_WIKI weighted
                copy_UAM = copy_UAM_and_remove_artists(UAM, u, user_artists_idx[test_artists_idx])
                dict_recommended_artists_idx = recommender.hybrid([
                    recommender.content_based(AAM_WIKI, user_artists_idx[train_artists_idx], KNN_CB, K_CB),
                    recommender.collaborative_filtering(copy_UAM, u, user_artists_idx[train_artists_idx], K_CF, KNN_CF)
                ], no_artists, K_HR, [1,1.7])

            elif type == "HR_CF_UUM_CF":     # hybrid of CF and CF_UUM
                copy_UAM = copy_UAM_and_remove_artists(UAM, u, user_artists_idx[test_artists_idx])
                dict_recommended_artists_idx = recommender.hybrid([
                    recommender.collaborative_filtering(copy_UAM, u, user_artists_idx[train_artists_idx], 2*K_CF, KNN_CF, UUM=UUM),
                    recommender.collaborative_filtering(copy_UAM, u, user_artists_idx[train_artists_idx], 2*K_CF, KNN_CF)
                ], no_artists, K_HR)

            elif type == "HR_CF_UUM_CB_WIKI":     # hybrid of CF_UUM and CB_WIKI
                copy_UAM = copy_UAM_and_remove_artists(UAM, u, user_artists_idx[test_artists_idx])
                dict_recommended_artists_idx = recommender.hybrid([
                    recommender.content_based(AAM_WIKI, user_artists_idx[train_artists_idx], KNN_CB, K_CB),
                    recommender.collaborative_filtering(copy_UAM, u, user_artists_idx[train_artists_idx], K_CF, KNN_CF, UUM=UUM)
                ], no_artists, K_HR)

            elif type == "HR_RBA_RBU":     # hybrid of RB_A and RB_U
                copy_UAM = copy_UAM_and_remove_artists(UAM, u, user_artists_idx[test_artists_idx])
                dict_recommended_artists_idx = recommender.hybrid([
                    recommender.random_baseline_user(u, np.setdiff1d(UAM[u, :], user_artists_idx[train_artists_idx]), copy_UAM, K_RB),
                    recommender.random_baseline_artist(np.setdiff1d(range(0, no_artists), user_artists_idx[train_artists_idx]), K_RB)
                ], no_artists, K_HR)

            elif type == "HR_CF_CF_UUM_CB_MOODS_CB_WIKI":     # hybrid of CF_UUM, CF, CB_MOODS and CB_WIKI
                copy_UAM = copy_UAM_and_remove_artists(UAM, u, user_artists_idx[test_artists_idx])
                dict_recommended_artists_idx = recommender.hybrid([
                   recommender.content_based(AAM_WIKI, user_artists_idx[train_artists_idx], KNN_CB, K_CB),
                   recommender.content_based(AAM_MOODS, user_artists_idx[train_artists_idx], KNN_CB, K_CB),
                   recommender.collaborative_filtering(copy_UAM, u, user_artists_idx[train_artists_idx], K_CF, KNN_CF, UUM=UUM),
                   recommender.collaborative_filtering(copy_UAM, u, user_artists_idx[train_artists_idx], K_CF, KNN_CF)
                ], no_artists, K_HR)           

            elif type == "HR_CF_CB_MOODS_CB_WIKI":     # hybrid of CF, CB_MOODS and CB_WIKI
                copy_UAM = copy_UAM_and_remove_artists(UAM, u, user_artists_idx[test_artists_idx])
                dict_recommended_artists_idx = recommender.hybrid([
                   recommender.content_based(AAM_WIKI, user_artists_idx[train_artists_idx], KNN_CB, K_CB),
                   recommender.content_based(AAM_MOODS, user_artists_idx[train_artists_idx], KNN_CB, K_CB),
                   recommender.collaborative_filtering(copy_UAM, u, user_artists_idx[train_artists_idx], K_CF, KNN_CF)
                ], no_artists, K_HR)

            elif type == "HR_CF_CB_MOODS_CB_WIKI_weighted":     # hybrid of CF, CB_MOODS and CB_WIKI weighted
                copy_UAM = copy_UAM_and_remove_artists(UAM, u, user_artists_idx[test_artists_idx])
                dict_recommended_artists_idx = recommender.hybrid([
                   recommender.content_based(AAM_WIKI, user_artists_idx[train_artists_idx], KNN_CB, K_CB),
                   recommender.content_based(AAM_MOODS, user_artists_idx[train_artists_idx], KNN_CB, K_CB),
                   recommender.collaborative_filtering(copy_UAM, u, user_artists_idx[train_artists_idx], K_CF, KNN_CF)
                ], no_artists, K_HR, [2,1,2.5])

            elif type == "HR_CF_CF_UUM_CB_WIKI":     # hybrid of CF_UUM, CF and CB_WIKI
                copy_UAM = copy_UAM_and_remove_artists(UAM, u, user_artists_idx[test_artists_idx])
                dict_recommended_artists_idx = recommender.hybrid([
                    recommender.content_based(AAM_WIKI, user_artists_idx[train_artists_idx], KNN_CB, K_CB),
                    recommender.collaborative_filtering(copy_UAM, u, user_artists_idx[train_artists_idx], K_CF, KNN_CF, UUM=UUM),
                    recommender.collaborative_filtering(copy_UAM, u, user_artists_idx[train_artists_idx], K_CF, KNN_CF)
                ], no_artists, K_HR)

            elif type == "HR_CF_CF_UUM_CB_WIKI_weighted":     # hybrid of CF_UUM, CF and CB_WIKI weighted
                copy_UAM = copy_UAM_and_remove_artists(UAM, u, user_artists_idx[test_artists_idx])
                dict_recommended_artists_idx = recommender.hybrid([
                    recommender.content_based(AAM_WIKI, user_artists_idx[train_artists_idx], KNN_CB, K_CB),
                    recommender.collaborative_filtering(copy_UAM, u, user_artists_idx[train_artists_idx], K_CF, KNN_CF, UUM=UUM),
                    recommender.collaborative_filtering(copy_UAM, u, user_artists_idx[train_artists_idx], K_CF, KNN_CF)
                ], no_artists, K_HR, [1,1.7,0.915])

            elif type == "HR_CF_CF_UUM_CB_MOODS":     # hybrid of CF_UUM, CF and CB_MOODS
                copy_UAM = copy_UAM_and_remove_artists(UAM, u, user_artists_idx[test_artists_idx])
                dict_recommended_artists_idx = recommender.hybrid([
                   recommender.content_based(AAM_MOODS, user_artists_idx[train_artists_idx], KNN_CB, K_CB),
                   recommender.collaborative_filtering(copy_UAM, u, user_artists_idx[train_artists_idx], K_CF, KNN_CF, UUM=UUM),
                   recommender.collaborative_filtering(copy_UAM, u, user_artists_idx[train_artists_idx], K_CF, KNN_CF)
                ], no_artists, K_HR)

            elif type == "HR_all5":     # hybrid of CF_UUM, CF, PB, CB_MOODS and CB_WIKI
                copy_UAM = copy_UAM_and_remove_artists(UAM, u, user_artists_idx[test_artists_idx])
                dict_recommended_artists_idx = recommender.hybrid([
                   recommender.content_based(AAM_WIKI, user_artists_idx[train_artists_idx], KNN_CB, K_CB),
                   recommender.content_based(AAM_MOODS, user_artists_idx[train_artists_idx], KNN_CB, K_CB),
                   recommender.collaborative_filtering(copy_UAM, u, user_artists_idx[train_artists_idx], K_CF, KNN_CF, UUM=UUM),
                   recommender.collaborative_filtering(copy_UAM, u, user_artists_idx[train_artists_idx], K_CF, KNN_CF),
                   recommender.popularity_based(copy_UAM, K_PB)
                ], no_artists, K_HR) 

            # Distill recommended artist indices from dictionary returned by the recommendation functions
            recommended_artists_idx = [idx for idx, score in dict_recommended_artists_idx]

            if VERBOSE:
                print "Recommended items: ", len(recommended_artists_idx)


            # Compute performance measures
            correct_artists_idx = np.intersect1d(user_artists_idx[test_artists_idx], recommended_artists_idx)          # correctly predicted artists
            # True Positives is amount of overlap in recommended artists and test artists
            TP = len(correct_artists_idx)
            # False Positives is recommended artists minus correctly predicted ones
            FP = len(np.setdiff1d(recommended_artists_idx, correct_artists_idx))

            # Precision is percentage of correctly predicted among predicted
            # Handle special case that not a single artist could be recommended -> by definition, precision = 100%
            if len(recommended_artists_idx) == 0:
                precision = 100.0
            else:
                precision = 100.0 * TP / len(recommended_artists_idx)

            # Recall is percentage of correctly predicted among all listened to
            # Handle special case that there is no single artist in the test set -> by definition, recall = 100%
            if len(test_artists_idx) == 0:
                recall = 100.0
            else:
                recall = 100.0 * TP / len(test_artists_idx)


            # add precision and recall for current user and fold to aggregate variables
            avg_precision += precision
            avg_recall += recall

            # Output precision and recall of current fold
            if VERBOSE:
                print ("\tPrecision: %.2f, Recall:  %.2f" % (precision, recall))

            # Increase fold counter
            fold += 1


    # Calculate avg precision for all users and folds
    avg_precision /= (NUMBER_OF_FOLDS * user_count)
    avg_recall /= (NUMBER_OF_FOLDS * user_count)

    # Calculate F-Measure
    if (avg_precision + avg_recall == 0):
        f_measure = 0
    else:
        f_measure = 2 * (avg_precision * avg_recall / (avg_precision + avg_recall))


    # Output mean average precision and recall
    if VERBOSE:
        print ("\nMAP: %.2f, MAR  %.2f, F %.2f" % (avg_precision, avg_recall, f_measure))
    else:
        print ("%.3f, %.3f, %.3f" % (avg_precision, avg_recall, f_measure))


def range_run(types=["RB_A"], no_of_users=99999, start=5, end=100, step=1):
    print ("recommender, number_of_users, number_of_recommended_items, avg_precision, avg_recall, f_measure")
    for type in types:
        # if type not in ["RB_A", "RB_U", "CF", "CB", "HR"]:
        #     continue

        for K in range(start, end, step):

            global K_RB, K_CF, K_CB, K_HR, K_PB

            sys.stderr.write("\r\t\t\tK_{1}: {0}/{2}".format(K, type, end))
            sys.stderr.flush()

            K_RB = K_CF = K_CB = K_HR = K_PB = K

            print (type + ", " + str(no_of_users) + ", " + str(K) + ","),
            run(type, no_of_users)


if __name__ == '__main__':

    artists = read_from_file(ARTISTS_FILE)
    users = read_from_file(USERS_FILE)
    UAM = np.loadtxt(UAM_FILE, delimiter='\t', dtype=np.float32)
    UUM = np.loadtxt(UUM_FILE, delimiter='\t', dtype=np.float32)
    AAM_WIKI = np.load(AAM_FILE_WIKI)
    AAM_MOODS = np.load(AAM_FILE_MOODS)

    K_RB = 30
    K_CF = 50
    K_CB = 50
    K_HR = 50
    K_PB = 30
    KNN_CB = 25
    KNN_CF = 25

    #run("CB_WIKI", 10)

    range_run(types=["HR_all5"], start=3, end=147, step=6)

