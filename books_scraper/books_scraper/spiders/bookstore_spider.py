import scrapy
from books_scraper.items import BookItem
from books_scraper.services.extractors import BookExtractor, CategoryExtractor
from books_scraper.services.selectors import RandomSelector

"""Crawls random categories and 5 random books from each."""
class BookstoreSpider(scrapy.Spider):


    name = "bookstore"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/index.html"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.selector = RandomSelector()

"""Discover all categories, then randomly pick 5-10."""
    def parse(self, response):
        categories = CategoryExtractor.extract(response)
        self.logger.info("Discovered %d categories", len(categories))
        chosen = self.selector.choose_categories(categories)
        self.logger.info("Selected categories: %s", [c[0] for c in chosen])
        for name, url in chosen:
            yield response.follow(url, self.parse_category,
                                  cb_kwargs={"category": name, "book_urls": []})

"""Collect ALL book URLs across pagination, then sample 5."""
    def parse_category(self, response, category, book_urls):

        book_urls = book_urls + [
            response.urljoin(h)
            for h in response.css("article.product_pod h3 a::attr(href)").getall()
        ]
        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, self.parse_category,
                                  cb_kwargs={"category": category, "book_urls": book_urls})
            return
        picked = self.selector.choose_books(book_urls, 5)
        self.logger.info("Category %s: %d books, picked %d", category, len(book_urls), len(picked))
        for url in picked:
            yield scrapy.Request(url, self.parse_book, cb_kwargs={"category": category},
                                 errback=self.on_error)

""" Extract fields from the detail page."""
    def parse_book(self, response, category):

        data = BookExtractor.extract(response)
        data["category"] = data["category"] or category
        yield BookItem(**data)

    def on_error(self, failure):
        self.logger.error("Request failed: %s", failure.request.url)