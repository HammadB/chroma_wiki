import pywikibot
import queue
from wikidb import WikipediaDatabase
from pathlib import Path
from datetime import datetime
import wikitextparser as wtp
from config import settings
import os
from tqdm import tqdm

SEED = "History_of_technology"
WIKI_DB_SAVE_PATH = Path("wikipedia_db_saves/")
INDEX_SAVE_PATH = Path("index_saves/")
SCRAPE_COUNT = 1000

os.environ["OPENAI_API_KEY"] = settings.openai_api_key

if __name__ == "__main__":
    # Scrape the data we want to index
    site = pywikibot.Site('en', 'wikipedia')

    # TODO parallelize
    def scrape(root: pywikibot.page._page.Page, max_count=10):
        frontier = queue.Queue()
        visited = set()
        frontier.put(root)
        visited.add(root)
        while not frontier.empty():
            current = frontier.get()
            for link in current.linkedPages(follow_redirects=True):
                if link not in visited:
                    visited.add(link)
                    frontier.put(link)
                    # Don't include root in max_count
                    if len(visited) == max_count + 1:
                        return list(visited)
        return visited

    visited = scrape(pywikibot.Page(site, "Apollo"), max_count=SCRAPE_COUNT)
    print(f"Scraped {len(visited)} pages")
    page_titles = [page.title() for page in visited]

    # Add
    wikidb = WikipediaDatabase()
    for page_title in tqdm(page_titles):
        page = wikidb.get_page(page_title)
        if page:
            wikidb.add_page(page_title, page)
    
    # Save
    now = datetime.now()
    filename = now.strftime("%m_%d_%Y_%H_%M_%S")
    WIKI_DB_SAVE_PATH.mkdir(exist_ok=True)
    INDEX_SAVE_PATH.mkdir(exist_ok=True)
    wikidb.save(str(WIKI_DB_SAVE_PATH / filename), str(INDEX_SAVE_PATH / filename))
