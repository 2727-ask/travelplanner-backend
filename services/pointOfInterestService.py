from datetime import datetime
from services.sparqlService import SPARQLService
from schemas.poi_query_schema import POIQuerySchema
import os

class PointOfInterestService:
    def __init__(self, lat, long, radius, preferences, visited_places):
        self.poi_schedule = {
            "morning": ["Trail", "Summit",  "Valley", "Museums", "Church", "Temple"],
            "afternoon": ["Museums", "Art gallery", "Market", "Shopping", "Beach"],
            "evening": ["Market", "Shopping", "Theater", "Garden", "Botanical", "Church", "Beach"],
            "night": ["Club", "Beach"]
        }

        self.lat = lat
        self.long = long
        self.radius = radius
        self.preferences = preferences
        self.limit = os.getenv("DEFAULT_LIMIT")
        self.visited_places = visited_places
        self.query = POIQuerySchema(latitude=lat, longitude=long, travel_radius=self.radius, result_limit=self.limit, feature_types=preferences, visited_places=self.visited_places).getQuerySchema()
        # print(self.query)

    def get_time_of_day(self, time_stamp):
        # Convert the time_stamp to a datetime object
        time = datetime.strptime(time_stamp, "%H:%M")
        
        # Define time ranges for each part of the day
        morning_start = datetime.strptime("06:00", "%H:%M")
        morning_end = datetime.strptime("11:59", "%H:%M")
        
        afternoon_start = datetime.strptime("12:00", "%H:%M")
        afternoon_end = datetime.strptime("17:59", "%H:%M")
        
        evening_start = datetime.strptime("18:00", "%H:%M")
        evening_end = datetime.strptime("20:59", "%H:%M")
        
        night_start = datetime.strptime("21:00", "%H:%M")
        night_end = datetime.strptime("23:59", "%H:%M")
        
        # Check which part of the day it is and return the corresponding POIs
        if morning_start <= time <= morning_end:
            return "morning"
        elif afternoon_start <= time <= afternoon_end:
            return "afternoon"
        elif evening_start <= time <= evening_end:
            return "evening"
        elif night_start <= time <= night_end:
            return "night"
        else:
            return None
        
    def get_suggested_pois(self, time_stamp):
        time_of_day = self.get_time_of_day(time_stamp)
        
        # Get the suggested POIs based on the time of day
        if time_of_day:
            return self.poi_schedule.get(time_of_day, [])
        else:
            return []
        
    def getDestination(self):
        self.sparql = SPARQLService(sparql_endpoint=os.getenv("SPARQL_ENDPOINT"),username=os.getenv("USERNAME"), password=os.getenv("PASSWORD")).getSparqlWrapper()
        self.sparql.setQuery(self.query)
        try:
            poi_data = []
            results = self.sparql.query().convert()
            for result in results["results"]["bindings"]:
                poi_info = {
                    "place": result['POI']['value'],
                    "name": result['name']['value'],
                    "type": result['type']['value'],
                    "distance": result['distance']['value'],
                    "geom": result['geom']['value']
                }
                poi_data.append(poi_info)  
            return poi_data    
        except Exception as e:
            print(f"An error occurred: {e}")
            return []     
           

