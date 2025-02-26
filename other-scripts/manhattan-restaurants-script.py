import requests
import time
import json
import os

YELP_API_KEY = os.environ['YELP_API_KEY']
API_URL = "https://api.yelp.com/v3/businesses/search"
HEADERS = {"Authorization": f"Bearer {YELP_API_KEY}", "accept": "application/json"}
CATEGORIES_OF_INTEREST = ["thai", "japanese", "chinese", "italian", "mexican"]
output_path = os.path.join(os.getcwd(), "manhattan_restaurants_cleaned.json")

LAT_MIN, LAT_MAX = 40.698, 40.882
LON_MIN, LON_MAX = -74.047, -73.906
MAX_CALLS = 2000
CUISINE_LIMIT = 150
CALL_COUNT = 0

def in_manhattan(zip_code):
    return zip_code.isdigit() and (10001 <= int(zip_code) <= 10282)

def fetch_restaurants(lat, lon, cuisine, radius=400, limit=40):
    global CALL_COUNT
    if CALL_COUNT >= MAX_CALLS:
        print("API call limit reached.")
        return []
    
    restaurants = []
    unique_ids = set()
    
    for offset in range(0, 240, limit):
        if CALL_COUNT >= MAX_CALLS or len(unique_ids) >= CUISINE_LIMIT:
            break
        
        params = {
            "latitude": lat,
            "longitude": lon,
            "radius": radius,
            "limit": limit,
            "categories": cuisine,
            "offset": offset,
            "sort_by": "best_match"
        }
        
        response = requests.get(API_URL, headers=HEADERS, params=params)
        CALL_COUNT += 1

        if response.status_code == 200:
            data = response.json()
            if not data.get("businesses"):
                #Call with the current offset doesn't give results so skipping next offset calls
                break
            for business in data.get("businesses", []):
                if not in_manhattan(business["location"].get("zip_code", "N/A")):
                    continue

                if business["id"] not in unique_ids and not business["is_closed"]:
                    unique_ids.add(business["id"])

                    category_titles = [
                        category["title"] for category in business.get("categories", [])
                    ]

                    restaurants.append({
                        "id": business["id"],
                        "name": business["name"],
                        "address": ", ".join(business["location"]["display_address"]),
                        "coordinates": business["coordinates"],
                        "categories": category_titles,
                        "review_count": business["review_count"],
                        "rating": business["rating"],
                        "zip_code": business["location"].get("zip_code", "N/A"),
                        "transactions": business.get("transactions", [])
                    })
        else:
            print(f"Error {response.status_code}: {response.json()}")
        
        time.sleep(0.5)
    
    return restaurants

def get_all_restaurants():
    all_restaurants = []
    unique_ids = set()
    
    lat_step, lon_step = 0.01, 0.01

    for cuisine in CATEGORIES_OF_INTEREST:
        cuisine_count = 0
        lat = LAT_MIN
        while lat <= LAT_MAX and CALL_COUNT < MAX_CALLS and cuisine_count < CUISINE_LIMIT:
            lon = LON_MIN
            while lon <= LON_MAX and CALL_COUNT < MAX_CALLS and cuisine_count < CUISINE_LIMIT:
                print(f"Fetching restaurants for lat: {lat}, lon: {lon}")
                new_restaurants = fetch_restaurants(lat, lon, cuisine)
                for res in new_restaurants:
                    if res["id"] not in unique_ids:
                        unique_ids.add(res["id"])
                        all_restaurants.append(res)
                        cuisine_count += 1
                lon += lon_step
            lat += lat_step
        
        print(f"Total {cuisine} restaurants fetched: {cuisine_count}")
    
    with open(output_path, "w") as f:
        json.dump(all_restaurants, f, indent=4)
    
    print(f"Total unique restaurants fetched: {len(all_restaurants)}, call count: {CALL_COUNT}")


get_all_restaurants()
