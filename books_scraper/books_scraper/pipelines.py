import logging
import re
import unicodedata
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
from books_scraper.storage.sqlite_repository import SQLiteBookRepository

logger = logging.getLogger(__name__)

"""Trims whitespace and normalizes unicode/spacing in text fields."""
class TextCleanPipeline:

    def process_item(self, item, spider):
        for field, value in item.items():
            if isinstance(value, str):
                value = unicodedata.normalize("NFKC", value)
                item[field] = re.sub(r"\s+", " ", value).strip()
        return item


"""Strips currency symbols and converts price to float."""
class PricePipeline:
    def process_item(self, item, spider):
        raw = item.get("price") or ""
        digits = re.sub(r"[^\d.]", "", raw)
        if not digits:
            raise DropItem(f"Invalid price: {raw!r}")
        item["price"] = float(digits)
        return item


"""In stock' -> True, anything else -> False."""
class AvailabilityPipeline:
    def process_item(self, item, spider):
        item["availability"] = str(item.get("availability", "")).lower().startswith("in stock")
        return item

"""Persists processed items into SQLite."""
class SQLitePipeline:
    
    def __init__(self, db_path):
        self.repo = SQLiteBookRepository(db_path)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings.get("SQLITE_PATH"))

    def open_spider(self, spider):
        self.repo.connect()
        logger.info("SQLite connected")

    def process_item(self, item, spider):
        self.repo.upsert(ItemAdapter(item).asdict())
        return item

    def close_spider(self, spider):
        self.repo.close()