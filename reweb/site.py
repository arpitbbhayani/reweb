import os
import json


class Site:
    def __init__(self, name, description, version, baseurl, keywords, author, **kwargs):
        self.name = name
        self.description = description
        self.version = version
        self.baseurl = baseurl
        self.keywords = keywords
        self.author = author
        self.data = {}

    def dict(self):
        return self.__dict__


def read_site():
    with open("reweb.json", "r") as fp:
        site = Site(**json.load(fp))
    for name in os.listdir("./data"):
        with open(os.path.join("./data", name)) as fp:
            metadata = json.load(fp)
            site.data[name.split(".")[0]] = metadata
    return site


def store_site(site):
    with open("reweb.json", "w") as fp:
        return fp.write(json.dumps(site.dict(), indent=4))
