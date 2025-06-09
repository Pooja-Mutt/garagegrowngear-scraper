# garagegrowngear-scraper

A Python Scrapy project that crawls and extracts product data (name, price, URL) from the Garage Grown Gear e-commerce site. Outputs clean JSON for analysis or portfolio use.

## Features

- Scrapes product name, price, and URL
- Outputs data as JSON
- Easy to extend for more fields

## How to Run

1. **Install requirements:**
   ```
   pip install scrapy
   ```

2. **Run the spider:**
   ```
   scrapy crawl garagegrowngear -o products.json
   ```

3. **(Optional) Convert to a pretty JSON array:**
   ```
   python convert_to_array.py
   ```

## Example Output

See `products_array.json` for a sample.

---

**Portfolio Project by [Pooja Mutt](https://github.com/Pooja-Mutt)**
