from lib.collector import collect_recipes, Persister

if __name__ == "__main__":
    # collect_urls("data/url.txt")
    persistor = Persister("data/recipe")
    collect_recipes(persistor, "data/url.txt")
