import json
import sys

input_file = "products.json"
output_file = "products_array.json"

with open(input_file, "r", encoding="utf-8") as f:
    data = json.load(f)

# If data is a dict, convert to array of values
if isinstance(data, dict):
    array_data = list(data.values())
else:
    array_data = data

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(array_data, f, indent=2, ensure_ascii=False)

print(f"Converted {input_file} to array and saved as {output_file}")