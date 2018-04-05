__author__ = "group_3"

import random
import numpy as np
from collections import OrderedDict


def random_baseline_artist(artists_idx, no_of_recommended_artists):
    # artists_idx                 list of artist indices to draw random sample from
    # no_of_recommended_artists   number of items to recommend

    random_artists_idx = random.sample(artists_idx, no_of_recommended_artists)

    # For random recommendations, all scores are equal
    random_artists_idx = {artist_idx: 1.0 for artist_idx in random_artists_idx}

    return random_artists_idx.items()



def random_baseline_user(user_idx, user_train_artists_idx, UAM, no_of_recommended_artists):
    # user_idx                      index of user
    # user_train_artists_idx        indices of users' training artists
    # UAM                           User Artist Matrix
    # no_of_recommended_artists     number of items to recommend

    users_idx = range(0, UAM.shape[0])
    users_idx.remove(user_idx)

    random_artists_idx = set([])

    while len(random_artists_idx) < no_of_recommended_artists:
        random_user_idx = random.choice(users_idx)

        random_user_artists_idx = np.nonzero(UAM[random_user_idx, :])[0]

        diff_random_artists_idx = set(np.setdiff1d(random_user_artists_idx, user_train_artists_idx))

        random_artists_idx = random_artists_idx.union(diff_random_artists_idx)

    # For random recommendations, all scores are equal
    rec_artists = {artist_idx: 1.0 for artist_idx in list(random_artists_idx)[:no_of_recommended_artists]}

    return rec_artists.items()

# Function that implements a PB recommender (popularity-based). It takes as input the UAM, computes the most popular
# artists and recommends them to the user, irrespective of their music preferences.
def popularity_based(UAM, no_of_recommended_artists):
    # UAM                           user-artist-matrix
    # no_of_recommended_artists     umber of artists to recommend

    # Ensure that number of available artists is not smaller than number of requested artists (excluding training set artists)
    no_artists = UAM.shape[1]
    if no_of_recommended_artists > no_artists:
        print str(no_of_recommended_artists) + " artists requested, but dataset contains only " + str(no_artists) + " artists! Reducing number of requested artists to " + str(no_artists) + "."
        no_of_recommended_artists = no_artists

    # get no_of_recommended_artists most popular artists, according to UAM
    UAM_sum = np.sum(UAM, axis=0)                                    # sum all (normalized) listening events per artist
    popsorted_aidx = np.argsort(UAM_sum)[-no_of_recommended_artists:]                        # indices of popularity-sorted artists (no_of_recommended_artists most popular artists)
    recommended_artists_idx = popsorted_aidx                         # artist indices
    recommended_artists_scores = UAM_sum[popsorted_aidx]             # corresponding popularity scores

    # Normalize popularity scores to range [0,1], to enable fusion with other approaches
    recommended_artists_scores = recommended_artists_scores / np.max(recommended_artists_scores)

    # Insert indices and scores into dictionary
    dict_recommended_artists_idx = {}
    for i in range(0, len(recommended_artists_idx)):
        dict_recommended_artists_idx[recommended_artists_idx[i]] = recommended_artists_scores[i]
#        print artists[recommended_artists_idx[i]] + ": " + str(recommended_artists_scores[i])

    # Return dictionary of recommended artist indices (and scores)
    return dict_recommended_artists_idx.items()


def collaborative_filtering(UAM, user_idx, user_train_artists_idx, no_of_recommended_artists, knn, UUM=None):
    # UAM                           User Artist Matrix
    # user_idx                      index of the user
    # user_train_artists_idx        indices of users' training artists
    # no_of_recommended_artists     number of items to recommend
    # knn                           k nearest neighbors to consider
    # [UUM]                         User User Matrix for getting KNN
    #                               if not available: get KNN from UAM only


    recommended_artists = {}

    # playcount vector for current user
    playcount_vector = UAM[user_idx, :]


    if UUM == None:
        # Compute similarities within UAM
        similarities_between_users = np.inner(playcount_vector, UAM)

        # Sort similarities to all others in ascending order
        sorted_index = np.argsort(similarities_between_users)
    else:
        # Get User from UUM
        user_vector = UUM[user_idx, :]

        # Sort UUM by similarities
        sorted_index = np.argsort(user_vector)


    # Select the closest neighbor to seed user
    k_nearest_neighbors_index = sorted_index[-1-knn:-1]
    k_nearest_neighbors = {}


    # Get new Artists from Neighbors (artists the user has not yet listened to)
    for rank, neighbor_index in enumerate(k_nearest_neighbors_index):

        neighbors_artists_idx = np.nonzero(UAM[neighbor_index,:])

        # Find same artists of user and neighbors
        neighbors_and_users_artists = np.intersect1d(neighbors_artists_idx, user_train_artists_idx)

        k_nearest_neighbors[neighbor_index] = { "rank": rank }
        k_nearest_neighbors[neighbor_index].update({ "intersect_artists": neighbors_and_users_artists })

        # Find Artists not known by the user
        neighbors_without_users_artists = np.setdiff1d(neighbors_artists_idx, user_train_artists_idx)

        k_nearest_neighbors[neighbor_index].update({ "diff_artists": neighbors_without_users_artists })


    # Sort each neighbor for their artist ranking (artists they most listened to)
    k_nearest_neighbors_sorted = sorted(k_nearest_neighbors.iteritems(), key=lambda (k,v): (len(v['intersect_artists']), -v['rank']), reverse=True)


    # Perform combined score ranking of artists recommended by neighbors
    idx = knn
    for neighbor, neighbors_artists in k_nearest_neighbors_sorted:

        for artist in neighbors_artists["diff_artists"]:


            # if a neighbor already listened this artist, add extra score points
            if artist in recommended_artists:
                recommended_artists[artist] += float(knn)/2

            # give points to an artist by the ranking position of the neighbor
            recommended_artists[artist] = float(recommended_artists.get(artist, 0)) + float(idx)/2

        idx -= 1


    # Sort recommended artists by their score points (decending)
    recommended_artists_sorted = sorted(recommended_artists.iteritems(), key=lambda (k,v): v, reverse=True)

    # Return list of recommended artist indices
    return recommended_artists_sorted[:no_of_recommended_artists]



def content_based(AAM, seed_artists_idx_train, artists_KNN, no_of_recommended_artists):

    seed_artists_similarities = AAM[seed_artists_idx_train,:]

    # Delete all Zerolines
    seed_artists_similarities_without_zerolines = seed_artists_similarities[~np.all(seed_artists_similarities == 0, axis=1)]

    # Get nearest neighbors of train set artist of seed user without zerolines
    # Sort AAM column-wise for each row
    sort_idx = np.argsort(seed_artists_similarities_without_zerolines, axis=1)

    # Select the K closest artists to all artists the seed user listened to
    neighbor_idx = sort_idx[:,-1-artists_KNN:-1]

    #print neighbor_idx

    # Scoring
    dict_recommended_artists_idx = {}

    neighbors_length = len(neighbor_idx)
    for nidx in neighbor_idx:
        scoreIdx = len(nidx)
        for n in nidx:

            if n in dict_recommended_artists_idx:
                    dict_recommended_artists_idx[n] += float(scoreIdx / 2) * float(neighbors_length)

            dict_recommended_artists_idx[n] = (float(dict_recommended_artists_idx.get(n, 0)) + float(scoreIdx) / 2) * float(neighbors_length)
            scoreIdx -= 1
        neighbors_length -= 1


    # Remove all artists that are in the training set of seed user
    for aidx in seed_artists_idx_train:
        dict_recommended_artists_idx.pop(aidx, None)            # drop (key, value) from dictionary if key (i.e., aidx) exists; otherwise return None

    # Sort by Score
    dict_recommended_artists_idx_sorted = sorted(dict_recommended_artists_idx.items(), key=lambda (k,v): v, reverse=True)


    # Return dictionary of recommended artist indices (and scores)
    return dict_recommended_artists_idx_sorted[:no_of_recommended_artists]



def hybrid(recommenders, no_of_artists, no_of_recommended_artists, score_weights = []):

    if len(recommenders) < 2:
        print "Hybrid Recommender requires two input recommenders!"
        return {}

    if len(score_weights) == 0:
        score_weights = [1] * len(recommenders)

    scores = np.zeros(shape=(len(recommenders), no_of_artists), dtype=np.float32)
    # Add scores from CB and CF recommenders to this matrix
    for i in range(len(recommenders)):
        for aidx, score in recommenders[i]:
            scores[i, aidx] = score

    # Normalize both Scores with Median
    scores_non_zero = []
    for i in range(len(recommenders)):
        scores_non_zero.append([x for x in scores[i] if x != 0.0])

    median_score = []
    for i in range(len(recommenders)):
        median_score.append(np.median(np.array(scores_non_zero[i])))

    normalization_factors = []
    for i in range(len(recommenders) - 1):
        normalization_factors.append(median_score[len(recommenders) - 1] / median_score[i])

    for i in range(len(recommenders) - 1):
        for aidx, score in recommenders[i]:
            scores[i, aidx] *= normalization_factors[i] * score_weights[i]

    for aidx, score in recommenders[len(recommenders) - 1]:
		scores[len(recommenders) - 1, aidx] = score * score_weights[len(recommenders) - 1]

    # Apply aggregation function (here, just take mean average of scores)
    scores_fused = np.mean(scores, axis=0)

    # Sort and select top no_of_recommended_artists to recommend
    sorted_idx = np.argsort(scores_fused)

    #print sorted_idx[-1-no_of_recommended_artists:-1]
    sorted_idx_top = sorted_idx[-1-no_of_recommended_artists:-1]

	# Put (artist index, score) pairs of highest scoring artists in a dictionary
    dict_recommended_artists_idx = {}
    for i in range(0, len(sorted_idx_top)):
        dict_recommended_artists_idx[sorted_idx_top[i]] = scores_fused[sorted_idx_top[i]]

    return dict_recommended_artists_idx.items()
