import json

with open("products.json", "r", encoding="utf-8") as infile:
    data = json.load(infile)

with open("products_array.json", "w", encoding="utf-8") as outfile:
    json.dump(data, outfile, indent=2)

print("Conversion complete! See products_array.json")