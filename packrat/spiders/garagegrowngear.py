import scrapy
import json
import re
from urllib.parse import urljoin

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
        # Try to get the product title from h1 or og:title meta tag
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
            variants = meta.get("product", {}).get("variants", [])

            seen_ids = set()
            for variant in variants:
                variant_id = variant.get("id")
                if variant_id in seen_ids:
                    continue
                seen_ids.add(variant_id)

                variant_title = variant.get("public_title") or "Default"
                price_cents = variant.get("price")

                if price_cents is not None:
                    price = f"${int(price_cents) / 100:.2f}"
                else:
                    html_price = response.css("span.price-item--regular::text").get()
                    if html_price is not None:
                        html_price = html_price.strip()
                        if html_price.lower().startswith("from"):
                            # Always get the minimum price from all variants
                            all_prices = [v.get("price") for v in variants if v.get("price") is not None]
                            if all_prices:
                                min_price = min(all_prices)
                                price = f"${int(min_price) / 100:.2f}"
                            else:
                                price = "N/A"
                        else:
                            price = html_price
                    else:
                        price = "N/A"

                # Safely handle None for title and variant_title
                safe_title = title.strip() if title else "No Title"
                safe_variant_title = variant_title.strip() if variant_title else "Default"

                # Only yield if price is not "From"
                if price and price.lower() != "from":
                    yield {
                        "productName": f"{safe_title} - {safe_variant_title}",
                        "price": price,
                        "url": url
                    }
        except Exception as e:
            self.logger.error(f"❌ Error parsing variant prices for {url}: {e}")