import json

with open('products_normalized_flat_clean.json', 'r', encoding='utf-8') as f:
    products = json.load(f)

flat_products = []
for product in products:
    # If your cleaned file is already flat, you might not need to flatten again!
    flat_products.append(product)

with open('products_normalized_flat.json', 'w', encoding='utf-8') as f:
    json.dump(flat_products, f, indent=2)