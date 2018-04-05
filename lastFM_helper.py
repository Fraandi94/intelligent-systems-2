__author__ = "group_3"

import requests

class LastFM:

    def __init__(self, API_key):
        self.API_key = API_key

    def request(self, method, params = {}):
        params["api_key"] = self.API_key
        params["method"] = method
        params["format"] = "json"
        return requests.get("http://ws.audioscrobbler.com/2.0/", params).json()
