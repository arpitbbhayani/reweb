class Site:
    def __init__(self, name, description, baseurl, keywords, author):
        self.name = name
        self.description = description
        self.baseurl = baseurl
        self.keywords = keywords
        self.author = author

    def dict(self):
        return self.__dict__
