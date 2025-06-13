import scrapy
import re
from urllib.parse import urljoin


class GarageGrownGearSpider(scrapy.Spider):
    name = "garagegrowngear"
    allowed_domains = ["garagegrowngear.com"]
    start_urls = ["https://www.garagegrowngear.com/collections/all?page=1"]

    custom_settings = {
        "DOWNLOAD_DELAY": 1.5,
        "FEED_EXPORT_ENCODING": "utf-8",
        "ROBOTSTXT_OBEY": False,
        "CONCURRENT_REQUESTS": 2,
        "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0",
    }

    def parse(self, response):
        # Get all product links
        links = response.css("a.product-item__title::attr(href)").getall()
        for link in links:
            full_url = response.urljoin(link)
            yield scrapy.Request(full_url, callback=self.parse_product)

        # Pagination
        next_page = response.css('a[title="Next"]::attr(href)').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_product(self, response):
        # Product name fallback using og:title
        name = response.css("h1.product__title::text").get()
        if not name:
            name = response.css("meta[property='og:title']::attr(content)").get()
        if name:
            name = name.strip()

        product_url = response.url

        # Categories from breadcrumb (skip 'Home')
        categories = response.css("nav.breadcrumb a::text").getall()
        categories = [c.strip() for c in categories if c.strip().lower() != "home"]
        if not categories:
            categories = ["All"]

        # Images
        images = response.css("img.product__media-img::attr(src)").getall()
        if not images:
            images = response.css("meta[property='og:image']::attr(content)").getall()
        images = [response.urljoin(img.strip()) for img in images if img.strip()]

        # Price
        price_text = response.css("span.price::text").get()
        price = price_text.strip().replace(" ", "") if price_text else None

        # Variants
        variants = []
        variant_options = response.css("select#ProductSelect-product-template option")
        if variant_options:
            for opt in variant_options:
                title = opt.css("::text").get(default="").strip()
                price_match = re.search(r"\$[\d.,]+", title)
                variant_price = price_match.group() if price_match else price
                variants.append({
                    "title": title.replace(variant_price, "").replace(" - ", "").strip() or "Default",
                    "price": variant_price,
                    "available": "sold out" not in title.lower()
                })
        else:
            variants = [{
                "title": "Default",
                "price": price,
                "available": True
            }]

        availability = "In Stock" if any(v["available"] for v in variants) else "Out of Stock"

        yield {
            "name": name or "",
            "productUrl": product_url,
            "categories": categories,
            "images": images,
            "price": price,
            "variants": variants,
            "techSpecs": [],
            "weight": "1",
            "weightUnit": "g",
            "reviewCount": 0,
            "availability": availability
        }
