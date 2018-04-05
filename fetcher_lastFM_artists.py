__author__ = "group_3"


import json
import csv
import sys
from LastFM_helper import LastFM
from collections import OrderedDict
from Queue import Queue
from threading import Thread


LASTFM_API_KEY = "4cb074e4b8ec4ee9ad3eb37d6f7eb240"
ARTISTS_FILE = "./data/C1ku/C1ku_idx_artists.txt"
ALL_ARTISTS_FILE = "./data/C1ku/LFM1b_artists.txt"


LastFM = LastFM(LASTFM_API_KEY)


artists = []
all_artists = {}
artists_extended = OrderedDict()
count = 0


with open(ARTISTS_FILE, 'r') as f:
    reader = csv.reader(f, delimiter='\t', quoting=csv.QUOTE_NONE)
    for row in reader:
        artists.append(row[0])


with open(ALL_ARTISTS_FILE, 'r') as f:
    reader = csv.reader(f, delimiter='\t', quoting=csv.QUOTE_NONE)
    for row in reader:
        all_artists[row[0]] = {"name": row[1]}


def get_mbid_for_artist(q):
    global count
    while True:
        artist_id = q.get()

        current = LastFM.request('artist.getInfo', {"artist": all_artists[artist_id]["name"]})
        current = current.get("artist").get("mbid", None)

        artists_extended[artist_id] = all_artists[artist_id]
        artists_extended[artist_id]["mbid"] = current or ""

        q.task_done()
        count += 1


        sys.stdout.write("\r{0}/{1} Artists fetched".format(count, len(artists)))
        sys.stdout.flush()


q = Queue(maxsize=0)
num_threads = 500

for artist_id in artists:
    artists_extended[artist_id] = None
    q.put(artist_id)

for i in range(num_threads):
    worker = Thread(target=get_mbid_for_artist, args=(q,))
    worker.setDaemon(True)
    worker.start()

q.join()


with open("data/C1ku_artists_extended.csv", "w") as f:
   f.write("id" + "\t" + "artist" + "\t" + "mbid" + "\n")
   for id, artist in artists_extended.items():
       f.write(id + "\t" + artist["name"] + "\t" + artist["mbid"].encode("utf-8") + "\n")
