# Collector

The collector is run to scrape for new recipes. 

It's responsibility is to scrape recipes and normalize them and store to disk. We don't load them straight into the database so we can 
we can manually correct any issues in the scraping and normalizing process. 

The collector is given a list of urls and a persister. The urls are the recipes to scrape and the persister handles write the collectors output to disk. 
Generally the persister won't overwrite a file that is already present.
