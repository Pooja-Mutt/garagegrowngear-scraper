import json

with open('products_normalized_flat.json', 'r', encoding='utf-8') as f:
    products = json.load(f)

for product in products:
    product.pop('description', None)
    product.pop('availability', None)
    product.pop('images', None)      # Remove images field
    product.pop('attributes', None)  # Remove attributes field

with open('products_normalized_flat_clean.json', 'w', encoding='utf-8') as f:
    json.dump(products, f, indent=2)