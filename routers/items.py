from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from services.itenaryService import IternaryService
from services.pointOfInterestService import PointOfInterestService
from models.VehicleEnum import Vehicle
from dotenv import load_dotenv
import os
import re
from typing import List

load_dotenv()

# Initialize the required configurations
sparql_endpoint = "http://localhost:7200/repositories/yelp-mapping-aditya"
current_location = "Red_Mango_420_S_Mill_Ave_Ste_107"
max_distance = 40000
rating_threshold = 3
restaurant_type = ["Mexican", "Italian"]
interests = ["Park", "Museum", "Lake", "Summit"]
result_limit = 10
latitude = 33.424564
longitude = -111.928001

# FastAPI application
app = FastAPI()

# Helper function to print values
def print_values(data):
    """ Prepare the data for sending over WebSocket """
    return {key: value for key, value in data.items()}

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

# Function to generate the itinerary and notify the client
async def generate_itinerary_and_notify(websocket: WebSocket, schedule_skeleton, interests, latitude, longitude, iternary_service):
    visitedPlaces = []
    visitedInterest = []
    coordinates = None
    current_suggestion = None
    poi_place = None

    await websocket.accept()  # Accept the WebSocket connection

    for item in schedule_skeleton:
        if item == 'food':
            food_place = iternary_service.getCurrentRestaurantBasedOnCoordinates(latitude=latitude, longitude=longitude)
            coordinates = getCoordinates(food_place.get('Geom'))
            data = print_values(food_place)
            await websocket.send_json(data)  # Send food place data to client
        else:
            # Traverse interests dynamically
            for interest in interests:
                if interest not in visitedInterest:
                    current_suggestion = [interest]  # Send one interest at a time
                    poi_place = iternary_service.getPOI(latitude=coordinates.get('latitude'), longitude=coordinates.get('longitude'), 
                                                         interest=current_suggestion, visited_places=visitedPlaces)
                    if poi_place:
                        coordinates = getCoordinates(poi_place.get('geom'))
                        visitedPlaces.append(f"itp:{poi_place.get('place').split('itp#')[1]}")
                        visitedInterest.append(interest)
                        data = print_values(poi_place)
                        await websocket.send_json(data)  # Send POI place data to client
                        break  # Found a POI, so move to the next item in the schedule
                    else:
                        print(f"No POI found for interest: {interest}. Marking as unvisited.")
    
    await websocket.close()  # Close the WebSocket connection

@app.websocket("/ws/itinerary")
async def websocket_endpoint(websocket: WebSocket):
    iternary = IternaryService(current_location=current_location, preferences=restaurant_type, rating_threshold=rating_threshold,
                               radius=max_distance, travelTime=8, vehicle=Vehicle.CAR, interests=place_schedular(interests))
    schedule_skeleton = ('food', 'place', 'food', 'place', 'food', 'place', 'food')

    # Generate the itinerary and notify the client via WebSocket
    await generate_itinerary_and_notify(websocket, schedule_skeleton, place_schedular(interests), latitude, longitude, iternary)
