import scrapy
import json
import re
from urllib.parse import urljoin
from w3lib.html import remove_tags

class GarageGrownGearSpider(scrapy.Spider):
    name = "garagegrowngear"
    custom_settings = {
        "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        "DOWNLOAD_DELAY": 5,
        "CONCURRENT_REQUESTS": 1,
        "ROBOTSTXT_OBEY": False,
    }
    start_urls = ["https://www.garagegrowngear.com/collections/all"]

    def parse(self, response):
        product_links = response.css("a.product-item__title::attr(href)").getall()
        seen_urls = set()
        for href in product_links:
            full_url = urljoin(response.url, href)
            if full_url not in seen_urls:
                seen_urls.add(full_url)
                yield response.follow(full_url, callback=self.parse_detail)

    def parse_detail(self, response):
        title = response.css("h1.product__title::text").get()
        if not title:
            title = response.css("meta[property='og:title']::attr(content)").get()
        url = response.url

        script_text = response.xpath('//script[contains(text(), "var meta =")]/text()').get()
        if not script_text:
            self.logger.warning(f"❌ No meta script found on: {url}")
            return

        try:
            match = re.search(r'var meta\s*=\s*(\{.*?\});', script_text, re.DOTALL)
            if not match:
                self.logger.warning(f"⚠️ meta JSON not found in script for: {url}")
                return

            meta_json = match.group(1)
            meta = json.loads(meta_json)
            product = meta.get("product", {})
            variants = product.get("variants", [])
            images = product.get("images", [])
            description = product.get("description")
            brand = product.get("vendor")
            category = product.get("type")
            product_id = product.get("id")
            tags = product.get("tags", [])
            options = product.get("options", [])

            # Fallback for images if empty
            if not images:
                images = response.css("img.product__media-img::attr(src)").getall()
                images = [response.urljoin(img) for img in images]

            # Clean description (remove HTML tags if needed)
            if description:
                description = remove_tags(description).strip()

            # Build variants list
            variants_list = []
            for v in variants:
                variants_list.append({
                    "id": v.get("id"),
                    "title": v.get("public_title") or "Default",
                    "price": f"${int(v.get('price')) / 100:.2f}" if v.get("price") else None,
                    "available": v.get("available")
                })

            # Main price (lowest variant price)
            prices = [int(v.get("price")) for v in variants if v.get("price")]
            main_price = f"${min(prices)/100:.2f}" if prices else None

            # Attributes: add tags, options, or other site-specific fields
            attributes = {}
            if tags:
                attributes["tags"] = tags
            if options:
                attributes["options"] = options

            yield {
                "id": product_id,
                "name": title,
                "brand": brand,
                "category": category,
                "price": main_price,
                "currency": "USD",
                "url": url,
                "images": images,
                "description": description,
                "attributes": attributes,
                "variants": variants_list,
                "availability": "In Stock" if any(v.get("available") for v in variants) else "Out of Stock",
                "extra": {}
            }

        except Exception as e:
            self.logger.error(f"❌ Error parsing product details for {url}: {e}")