import json

# 1) Load the original cities data
with open('cities.json', 'r', encoding='utf-8') as f:
    cities = json.load(f)

# 2) Build a mapping: city → "@lat,lon,14z"
coords_map = {
    item['city']: f"@{item['latitude']},{item['longitude']},14z"
    for item in cities
    if 'latitude' in item and 'longitude' in item
}

# 3) Write out the new JSON file
with open('coords.json', 'w', encoding='utf-8') as f:
    json.dump(coords_map, f, indent=2, ensure_ascii=False)

print(f"Generated latlong_coords.json with {len(coords_map)} entries.")
