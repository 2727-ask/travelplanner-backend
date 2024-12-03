from fastapi import FastAPI, WebSocket
from services.itenaryService import IternaryService
from services.pointOfInterestService import PointOfInterestService
from models.VehicleEnum import Vehicle
from dotenv import load_dotenv
import os
import re

load_dotenv()

# Configuration and initialization
sparql_endpoint = "http://localhost:7200/repositories/yelp-mapping-aditya"
current_location = "Red_Mango_420_S_Mill_Ave_Ste_107"
max_distance = 40000
rating_threshold = 3
restaurant_type = ["Mexican", "Italian"]
interests = ["Park", "Museum", "Lake", "Summit"]
result_limit = 10
latitude = 33.424564
longitude = -111.928001

# Helper function to print values
def print_values(data):
    print("-" * 30)
    for key, value in data.items():
        print(f"{key}: {value}")

# Sorting the places based on custom order
def place_schedular(places):
    custom_order = {
        "Summit": 0,
        "Trail": 1,
        "Valley": 2,
        "Church": 3,
        "Museum": 4,
        "Park": 5,
        "Shopping": 6,
        "Garden": 7,
        "Lake": 8
    }
    sorted_places = sorted(places, key=lambda place: custom_order.get(place, float('inf')))
    return sorted_places

# Extract coordinates from URL
def getCoordinates(url):
    match = re.search(r"POINT\((-?\d+\.\d+)_(-?\d+\.\d+)\)", url)

    if match:
        longitude = match.group(1)
        latitude = match.group(2)
        return {
            "longitude": longitude,
            "latitude": latitude
        }
    else:
        return None

# Asynchronous itinerary generation function
async def generate_itinerary(ws, schedule_skeleton, interests, current_location, restaurant_type, max_distance, rating_threshold, latitude, longitude):
    interests = place_schedular(interests)
    iternary = IternaryService(current_location=current_location, preferences=restaurant_type, rating_threshold=rating_threshold,
                               radius=max_distance, travelTime=8, vehicle=Vehicle.CAR, interests=interests)
    coordinates = None
    visitedPlaces = []
    visitedInterest = []
    itinerary_details = []

    for item in schedule_skeleton:
        if item == 'food':
            food_place = iternary.getCurrentRestaurantBasedOnCoordinates(latitude=latitude, longitude=longitude)
            coordinates = getCoordinates(food_place.get('Geom'))
            print_values(food_place)
            itinerary_details.append(food_place)
            # Send the data in real-time
            await ws.send_text(str(food_place))
        else:
            # Traverse interests dynamically
            for interest in interests:
                if interest not in visitedInterest:
                    current_suggestion = [interest]
                    poi_place = iternary.getPOI(latitude=coordinates.get('latitude'), longitude=coordinates.get('longitude'), 
                                                 interest=current_suggestion, visited_places=visitedPlaces)
                    if poi_place:
                        coordinates = getCoordinates(poi_place.get('geom'))
                        visitedPlaces.append(f"itp:{poi_place.get('place').split('itp#')[1]}")
                        visitedInterest.append(interest)
                        print_values(poi_place)
                        itinerary_details.append(poi_place)
                        # Send the data in real-time
                        await ws.send_text(str(poi_place))
                        break  # Move to the next item after finding a POI
                    else:
                        itinerary_details.append(f"No POI found for interest: {interest}. Marking as unvisited.")
                        # Send real-time message when no POI is found
                        await ws.send_text(f"No POI found for interest: {interest}. Marking as unvisited.")

    return itinerary_details


# FastAPI app with WebSocket endpoint
app = FastAPI()

@app.websocket("/ws/itinerary")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()

    # Sample schedule and interests for testing
    schedule_skeleton = ('food', 'place', 'food', 'place', 'food', 'place', 'food')
    interests = place_schedular(["Park", "Museum", "Lake", "Summit"])

    # Generate the itinerary and send data in real-time
    await generate_itinerary(ws, schedule_skeleton, interests, current_location, restaurant_type, max_distance, rating_threshold, latitude, longitude)

    await ws.close()
