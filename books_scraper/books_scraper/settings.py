import os
from pathlib import Path

BOT_NAME = "books_scraper"
SPIDER_MODULES = ["books_scraper.spiders"]
NEWSPIDER_MODULE = "books_scraper.spiders"

ROBOTSTXT_OBEY = True
DOWNLOAD_DELAY = 0.5
AUTOTHROTTLE_ENABLED = True
RETRY_ENABLED = True
LOG_LEVEL = "INFO"

OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "output")).resolve()
SQLITE_PATH = str(OUTPUT_DIR / "books.db")

ITEM_PIPELINES = {
    "books_scraper.pipelines.TextCleanPipeline": 100,
    "books_scraper.pipelines.PricePipeline": 200,
    "books_scraper.pipelines.AvailabilityPipeline": 300,
    "books_scraper.pipelines.SQLitePipeline": 400,
}

FIELDS = ["title", "price", "availability", "product_url", "image_url", "category"]
FEEDS = {
    str(OUTPUT_DIR / "books.json"): {"format": "json", "indent": 4, "overwrite": True, "fields": FIELDS},
    str(OUTPUT_DIR / "books.csv"):  {"format": "csv", "overwrite": True, "fields": FIELDS},
    str(OUTPUT_DIR / "books.xml"):  {"format": "xml", "overwrite": True, "fields": FIELDS},
}
FEED_EXPORT_ENCODING = "utf-8"