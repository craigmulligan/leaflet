from app.collector import collect_recipes, collect_urls, Persister

if __name__ == "__main__":
    """
    This fetchs recipes and saves them
    to data/*

    From there we can manually correct them if needed
    and then load into the db.

    NOTE: If any of the files exist, we don't overwrite them.
    This is so we can maintain manual fixes. If you want a file
    to be regenerated you must delete it from /data
    """
    url_file = "data/test.txt"
    persister = Persister()
    collect_urls(url_file)
    collect_recipes(persister, url_file)
