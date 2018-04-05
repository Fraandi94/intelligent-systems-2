__author__ = "group_3"

import musicbrainzngs
import requests
from bs4 import BeautifulSoup
import csv
import json
import os
import sys
from collections import OrderedDict

ARTISTS_MOODS_FILE = "data/C1ku/C1ku_artists_moods.csv"

reload(sys)
sys.setdefaultencoding("utf-8")

# get moods for an artist with musicbrainz id
def get_AMG_moods(mbid, artist):
    moods = []
    # check if musicbrainz artist page contains the allmusic url
    try:
      musicbrainzngs.set_useragent("MBZ-Fetcher", "0.2")
      musicbrainz_artist = musicbrainzngs.get_artist_by_id(mbid, includes="url-rels")

      url_relation_list = musicbrainz_artist["artist"].get("url-relation-list", {})
      all_music_url = ([url["target"] for url in url_relation_list if url and url.get("type") == "allmusic"] or [False])[0]

    except:
      all_music_url = False
      pass
    # if musicbrainz contains no allmusic url, search directly for moods on allmusic.com
    if not all_music_url:
        artist_name = artist
        try:
          # get allmusic search results
          AMG_searchpage = requests.get("http://www.allmusic.com/search/artists/" + artist, headers={"User-agent": "Mozilla/5.0"})
          soup = BeautifulSoup(AMG_searchpage.text, "html.parser")
          if not soup.find_all("div", class_="no-results"):
            search_results = soup.find("ul", class_="search-results")
            search_results_name = search_results.find_all("div", class_="name")
            for element in search_results_name:
              link = element.find("a", href=True)
              # check if first search result matches the artist name
              if link.string.lower() == artist_name.lower():
                all_music_url = link["href"]
                break
              else:
                return moods
          else:
            return moods
        except:
          return moods

    # call the allmusic page for the requested artist
    AMG_page = requests.get(all_music_url, headers={"User-agent": "Mozilla/5.0"})
    soup = BeautifulSoup(AMG_page.text, "html.parser")
    moods_section = soup.find("section", class_="moods")

    if not moods_section:
        return moods

    moods_elements = moods_section.find_all("a")

    # get all moods from the moods section
    for element in moods_elements:
        moods.append(element.string)

    return moods

# call get_AMG_moods for each artist and output log
def fetch_AMG_moods(artists):
    artists_and_moods = OrderedDict()
    idx = 0
    try:
      for id, artist in artists.items():
        moods = get_AMG_moods(artist["mbid"], artist["name"])
        artists_and_moods[id] = {"name": artist["name"], "moods": moods}

        idx += 1
        sys.stdout.write("\r{0}/{1} fetched".format(idx, len(artists)))
        sys.stdout.flush()
    except KeyboardInterrupt:
      pass
    finally:
      return artists_and_moods


# read range of artists from artists.csv
def getArtists(fromIdx, toIdx):
  artists = OrderedDict()
  with open("data/C1ku/C1ku_artists_extended.csv", 'r') as f:
    reader = csv.DictReader(f, delimiter='\t', quoting=csv.QUOTE_NONE)
    for i in range(fromIdx-1):
      next(reader)
    rangeSize = toIdx+1 - fromIdx
    for row in reader:
      if rangeSize > 0:
        artists[row["id"]] = {"name": row["artist"], "mbid": row["mbid"]}
      else:
        break
      rangeSize -= 1
  return artists

# add new moods to the moods file
def appendMoodsToFile(moods):
    f = open(ARTISTS_MOODS_FILE,'a')
    for id, artist in moods.items():
      f.write(str(id) + "\t" + artist["name"].encode('utf-8') + "\t" + ",".join(artist["moods"]).encode('utf-8') + "\n")
    f.close()


# check which moods are missing in moods.csv and begin fetching the remaining ones
def fetchMissingMoods():
  if os.path.exists(ARTISTS_MOODS_FILE):
    num_lines = sum(1 for line in open(ARTISTS_MOODS_FILE, "r"))
  else:
    num_lines = 0

  with open(ARTISTS_MOODS_FILE, "a+") as f:
    if num_lines == 0:
      f.write("id" + "\t" + "artist" + "\t" + "moods" + "\n")
      f.close()

  artists = getArtists(num_lines, 10123)
  moods = fetch_AMG_moods(artists)
  appendMoodsToFile(moods)
  print "\n done!"


# count all fetched moods, no. of artists with moods and average moods per artist with moods
# def countMoods():
#   counter = 0
#   moods_overall = 0
#   different_moods = []
#   with open(ARTISTS_MOODS_FILE, 'r') as f:
#     reader = csv.DictReader(f, delimiter='\t', quoting=csv.QUOTE_NONE)
#     for row in reader:
#       if row["moods"]:
#         artist_moods = row["moods"].split(",")
#         different_moods = list(set(different_moods) | set(artist_moods))
#         for mood in artist_moods:
#           moods_overall += 1
#         counter += 1
#     print "there exist", len(different_moods), "different moods"
#     print moods_overall, "moods fetched for", counter, "artists"
#     print moods_overall / counter, "moods per artist with moods"

fetchMissingMoods()

# countMoods()

