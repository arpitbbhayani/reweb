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
    
    basepath = "./data"
    for (root, _, filepaths) in os.walk(basepath):
        for path in filepaths:
            filepath = os.path.join(root, path)
            with open(filepath) as fp:
                if not filepath.endswith(".json"):
                    continue
                metadata = json.load(fp)
                relative_path = os.path.relpath(filepath, basepath)
                key = relative_path.replace("/", "_").split(".")[0]
                site.data[key] = metadata
    return site


def store_site(site):
    with open("reweb.json", "w") as fp:
        return fp.write(json.dumps(site.dict(), indent=4))
