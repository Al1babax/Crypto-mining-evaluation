import webscraper_lib as ws


scraper = ws.WebScraper("https://www.is.fi/", True)
scraper.open_website()
print(scraper.get_sourcecode())
