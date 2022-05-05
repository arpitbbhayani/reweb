import os
import json
import base64


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
                relative_path = os.path.relpath(filepath, basepath)
                key = relative_path.replace("/", "_").split(".")[0]
                if filepath.endswith(".json"):
                    content = json.load(fp)
                    site.data[key] = content

    basepath = "./static"
    for (root, _, filepaths) in os.walk(basepath):
        for path in filepaths:
            filepath = os.path.join(root, path)
            with open(filepath, 'rb') as fp:
                relative_path = os.path.relpath(filepath, basepath)
                key = relative_path.replace("/", "_").split(".")[0]
    
                if filepath.endswith(".svg"):
                    content = fp.read()
                    site.data[key] = str(base64.b64encode(content))[2:-1]
    return site


def store_site(site):
    with open("reweb.json", "w") as fp:
        data = site.dict()
        return fp.write(json.dumps({ k:v for k, v in data.items() if k != "data" }, indent=4))
