from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from services.itenaryService import IternaryService
from services.pointOfInterestService import PointOfInterestService
from models.VehicleEnum import Vehicle
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor
import os
import asyncio
import re
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

executor = ThreadPoolExecutor(max_workers=5)
sparql_endpoint = os.getenv("SPARQL_ENDPOINT")
print(sparql_endpoint)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # React's development server URL
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Pydantic model for parsing WebSocket request data
class ItineraryRequest(BaseModel):
    max_distance: int
    rating_threshold: float
    restaurant_type: list[str]
    interests: list[str]
    result_limit: int
    latitude: float
    longitude: float

# Helper functions
def print_values(data):
    print("-" * 30)
    for key, value in data.items():
        print(f"{key}: {value}")

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

def getCoordinates(url):
    match = re.search(r"POINT\((-?\d+\.\d+)_(-?\d+\.\d+)\)", url)
    if match:
        longitude = match.group(1)
        latitude = match.group(2)
        return {"longitude": longitude, "latitude": latitude}
    return None

async def run_blocking_io(func, *args):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, func, *args)

async def generate_itinerary(ws, schedule_skeleton, interests, iternary, latitude, longitude):
    coordinates = None
    visitedPlaces = []
    visitedInterest = []
    for item in schedule_skeleton:
        if item == 'food':
            food_place = await run_blocking_io(iternary.getCurrentRestaurantBasedOnCoordinates, latitude, longitude)
            coordinates = getCoordinates(food_place.get('Geom'))
            print_values(food_place)
            await ws.send_json(food_place)
        else:
            for interest in interests:
                if interest not in visitedInterest:
                    poi_place = await run_blocking_io(iternary.getPOI, coordinates.get('latitude'), coordinates.get('longitude'), [interest], visitedPlaces)
                    if poi_place:
                        coordinates = getCoordinates(poi_place.get('geom'))
                        visitedPlaces.append(f"itp:{poi_place.get('place').split('itp#')[1]}")
                        visitedInterest.append(interest)
                        print_values(poi_place)
                        await ws.send_json(poi_place)
                        break
                    else:
                        print(f"No POI found for interest: {interest}. Marking as unvisited.")
                        await ws.send_text(f"No POI found for interest: {interest}. Marking as unvisited.")

# WebSocket endpoint to stream itinerary
@app.websocket("/ws/itinerary")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    try:
        # Receive the request body as JSON
        data = await ws.receive_json()
        request = ItineraryRequest(**data)

        schedule_skeleton = ('food', 'place', 'food', 'place', 'food', 'place', 'food')
        interests = place_schedular(request.interests)

        iternary = IternaryService(
            preferences=request.restaurant_type,
            rating_threshold=request.rating_threshold,
            radius=request.max_distance,
            travelTime=8,
            vehicle=Vehicle.CAR,
            interests=interests
        )

        await generate_itinerary(ws, schedule_skeleton, interests, iternary, request.latitude, request.longitude)
    except WebSocketDisconnect:
        print("WebSocket disconnected")
    except Exception as e:
        print(f"Error: {e}")
        await ws.send_text(f"Error: {e}")
    finally:
        await ws.close()
