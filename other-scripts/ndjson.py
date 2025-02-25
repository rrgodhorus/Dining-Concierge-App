import json
import os

cwd = os.getcwd()
input_file = os.path.join(cwd, "manhattan_restaurants(150*5).json")
output_file = os.path.join(cwd, "restaurants_bulk.ndjson")

if not os.path.exists(input_file):
    print(f"Error: File '{input_file}' not found in the current working directory.")
    exit(1)

with open(input_file, "r") as f:
    restaurants = json.load(f)

bulk_data = []
for restaurant in restaurants:
    action = {
        "index": {
            "_index": "restaurants",
            "_id": restaurant["id"]  
        }
    }
    bulk_data.append(json.dumps(action))

    data = {
        "RestaurantID": restaurant["id"],
        "Cuisine": restaurant["categories"] 
    }
    bulk_data.append(json.dumps(data))

with open(output_file, "w") as f:
    for line in bulk_data:
        f.write(line + "\n")

print(f"Bulk NDJSON file created: {output_file}")