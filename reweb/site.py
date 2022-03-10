import json


class Site:
    def __init__(self, name, description, version, baseurl, keywords, author):
        self.name = name
        self.description = description
        self.version = version
        self.baseurl = baseurl
        self.keywords = keywords
        self.author = author

    def dict(self):
        return self.__dict__


def read_site():
    with open("reweb.json", "r") as fp:
        return Site(**json.load(fp))


def store_site(site):
    with open("reweb.json", "w") as fp:
        print(site.dict())
        return fp.write(json.dumps(site.dict(), indent=4))
