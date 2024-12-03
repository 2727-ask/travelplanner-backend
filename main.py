from fastapi import FastAPI, WebSocket
from services.itenaryService import IternaryService
from services.pointOfInterestService import PointOfInterestService
from models.VehicleEnum import Vehicle
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor
import os

load_dotenv()

executor = ThreadPoolExecutor(max_workers=5)
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

app = FastAPI()

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

import re

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

async def run_blocking_io(func, *args):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, func, *args)

# Function to generate itinerary and push data to WebSocket
async def generate_itinerary(ws, schedule_skeleton, interests, iternary, latitude, longitude):
    coordinates = None
    visitedPlaces = []
    visitedInterest = []
    for item in schedule_skeleton:
        if item == 'food':
            food_place = await run_blocking_io(iternary.getCurrentRestaurantBasedOnCoordinates, latitude, longitude)
            coordinates = getCoordinates(food_place.get('Geom'))
            print_values(food_place)
            # Send the food place data via WebSocket
            await ws.send_json(food_place)
        else:
            # Traverse interests dynamically
            for interest in interests:
                if interest not in visitedInterest:
                    current_suggestion = [interest]  # Send one interest at a time
                    poi_place = await run_blocking_io(iternary.getPOI, coordinates.get('latitude'), coordinates.get('longitude'), current_suggestion, visitedPlaces)
                    if poi_place:
                        coordinates = getCoordinates(poi_place.get('geom'))
                        visitedPlaces.append(f"itp:{poi_place.get('place').split('itp#')[1]}")
                        visitedInterest.append(interest)
                        print_values(poi_place)
                        # Send the POI place data via WebSocket
                        await ws.send_json(poi_place)
                        break  # Found a POI, so move to the next item in the schedule
                    else:
                        print(f"No POI found for interest: {interest}. Marking as unvisited.")
                        # Send unvisited data via WebSocket
                        await ws.send_text(f"No POI found for interest: {interest}. Marking as unvisited.")

# WebSocket endpoint to stream itinerary
import time
import asyncio
@app.websocket("/ws/itinerary")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    await asyncio.sleep(2)

    
    schedule_skeleton = ('food', 'place', 'food', 'place', 'food', 'place', 'food')
    interests = place_schedular(["Park", "Museum", "Lake", "Summit"])
    iternary = IternaryService(current_location=current_location, preferences=restaurant_type, rating_threshold=rating_threshold,
                               radius=max_distance, travelTime=8, vehicle=Vehicle.CAR, interests=interests)
    
    # Generate the itinerary and send data in real-time
    await generate_itinerary(ws, schedule_skeleton, interests, iternary, latitude, longitude)

    await ws.close()

