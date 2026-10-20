from typing import List, Tuple
from scrapy.http import Response

""" Discovers categories from the homepage sidebar (no hardcoding)."""
class CategoryExtractor:

    SELECTOR = "div.side_categories ul li ul li a"

    @classmethod
    def extract(cls, response: Response) -> List[Tuple[str, str]]:
        return [
            (a.css("::text").get("").strip(), response.urljoin(a.attrib["href"]))
            for a in response.css(cls.SELECTOR)
        ]

"""Extracts book fields from a product detail page."""
class BookExtractor:

    @staticmethod
    def extract(response: Response) -> dict:
        return {
            "title": response.css("div.product_main h1::text").get(),
            "price": response.css("div.product_main p.price_color::text").get(),
            "availability": " ".join(response.css("div.product_main p.availability::text").getall()),
            "product_url": response.url,
            "image_url": response.urljoin(response.css("div.item.active img::attr(src)").get("")),
            "category": response.css("ul.breadcrumb li:nth-child(3) a::text").get(),
        }