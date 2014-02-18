def wikipedia(self, string):
    import requests
    UA = "JiyuuBot/1 (http://github.com/JiyuuProject/JiyuuBot; bob@bob131.so) BasedOnRequests/%s" % requests.__version__
    matches = re.findall("https+://(\w+).wikipedia.org/wiki/(\w+)", string)
    for match in matches:
        categories = requests.get("http://%s.wikipedia.org/w/api.php?action=query&prop=categories&format=json&cllimit=10&cldir=descending&titles=%s&redirects=" % match, headers={"user-agent": UA}).json()["query"]["pages"]
        if "missing" in categories.keys():
            self.conman.gensend("Page not found")
        else:
            self.conman.gensend("%s | Categories: %s" % (categories["title"], ", ".join(x["title"].replace("Categories:", "") for x in categories["categories"])))

self._map("regex", "https+://(\w+).wikipedia.org/wiki/(\w+)", wikipedia, "Wikipedia")
