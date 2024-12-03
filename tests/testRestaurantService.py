from services.itenaryService import IternaryService
from models.VehicleEnum import Vehicle
from dotenv import load_dotenv


load_dotenv()


sparql_endpoint = "http://localhost:7200/repositories/yelp-mapping-aditya"
current_location = "Red_Mango_420_S_Mill_Ave_Ste_107"
max_distance = 40000
rating_threshold = 3
restaurant_type = ["Chinese", "Veg", "Indian"]
result_limit = 40
latitude = 33.424564
longitude = -111.928001


print("-"*50)
iternary = IternaryService(current_location=current_location, preferences=restaurant_type, rating_threshold=rating_threshold,radius=max_distance, travelTime=8, vehicle=Vehicle.CAR)
restaurant1 = iternary.getCurrentRestaurantBasedOnCoordinates(latitude=latitude, longitude=longitude)
for key, value in restaurant1.items():
    print(f"{key}: {value}")

    


