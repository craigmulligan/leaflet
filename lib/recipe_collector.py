class RecipeCollector:
    """
    Recipe Collector is responsible
    for fetching websites and dumping them into
    the sqlite db. Therefore it's never run on the
    server.
    """

    def __init__(self, db, urls) -> None:
        self.urls = urls
        self.db = db

    def run(self):
        pass
