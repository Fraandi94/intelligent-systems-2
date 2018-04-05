__author__ = "group_3"

import wikipedia
import csv
import os
import sys
from collections import OrderedDict
from difflib import SequenceMatcher
import unicodedata


ARTISTS_FILE = "data/C1ku/C1ku_artists_extended.csv"
ARTISTS_WIKILINKS_FILE = "data/C1ku/C1ku_artists_wikilinks.csv"


class WikipediaPage(wikipedia.WikipediaPage):
    pass

    @property
    def linkshere(self):
        '''
        List of titles of Wikipedia page links leading to a page.

        .. note:: Only includes articles from namespace 0, meaning no Category, User talk, or other meta-Wikipedia pages.
        '''

        if not getattr(self, '_linkshere', False):
            self._linkshere = [
            link['title']
            for link in self.__continued_query({
              'prop': 'linkshere',
              'lhnamespace': 0,
              'lhlimit': 'max'
            })
            ]

        return self._linkshere


def get_wiki_links(artist):

    whitelist = ["band", "singer", "musician", "rapper", "producer", "pop", "rock", "duo", "trio", "composer", "DJ"]

    def get_wiki_page(query):
        try:
            page = WikipediaPage(search_result)
        except wikipedia.exceptions.DisambiguationError as e:
            ambiguous_titles = e.options
            title = [title for title in ambiguous_titles if any("(" + word + ")" in title.lower() for word in whitelist)]
            if title:
                try:
                    page = WikipediaPage(title[0])
                except wikipedia.exceptions.PageError:
                    return False
            else:
                return False

        if any(word in page.summary for word in whitelist):
            return page
        else:
            return False


    search_results = wikipedia.search(artist)

    if not search_results:
        return []

    search_result = search_results[0]
    page = get_wiki_page(search_result)

    if not page:
        search_result = [title for title in search_results if any("(" + word + ")" in title.lower() for word in whitelist)]
        if search_result:
            search_result = search_result[0]
            page = get_wiki_page(search_result)
            if not page: return []
        else:
            return []

    # Check if Artist is not Lowercase or Uppercase (must be foreign then)
    if unicodedata.category(artist.decode("UTF8")[0]) != "Lo":
        # Check String Similarity and return empty when lower than 0.3
        if SequenceMatcher(None, artist.lower(), page.title.lower()).ratio() < 0.3:
            return []

    #print artist, " - ", page.title.encode("utf-8")

    try:
        links = page.links
        links += page.linkshere
        links = [l.encode('UTF8') for l in links]
    except:
        return []

    return (page.title, set(links))


def fetch_and_write_wiki_links(artists):

    if os.path.exists(ARTISTS_WIKILINKS_FILE):
        num_lines = sum(1 for line in open(ARTISTS_WIKILINKS_FILE, "r"))
    else:
        num_lines = 0

    with open(ARTISTS_WIKILINKS_FILE, "a+") as f:
        if num_lines == 0:
            f.write("id" + "\t" + "artist" + "\t" + "page_title" + "\t" + "links" + "\n")

        for idx, (id, artist) in enumerate(artists.items()):
            if idx < num_lines:
                continue

            titles_and_links = get_wiki_links(artist)
            if titles_and_links:
                title = titles_and_links[0]
                links = titles_and_links[1]
            else:
                title = ""
                links = ""
            f.write(id + "\t" + artist + "\t" + title.encode("utf-8") + "\t" + ",".join(links) + "\n")

            sys.stdout.write("\r{0}/{1} fetched".format(idx+1, len(artists)))
            sys.stdout.flush()

    print "Finished!"




artists = OrderedDict()
with open(ARTISTS_FILE, 'r') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        artists[row["id"]] = row["artist"]

fetch_and_write_wiki_links(artists)

