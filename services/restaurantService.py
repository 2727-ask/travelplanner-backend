from schemas.restaurants_query_schema import RestaurantQuerySchema
from services.sparqlService import SPARQLService
import os

class RestaurantService:
    def __init__(self, lat=None, long=None, current_location=None, radius=None, rating_threshold=None, preferences=None, visited_restaurant=None, limit=None):
        if(lat != None and long != None):
            self.lat = lat
            self.long = long
            self.radius = radius
            self.rating_threshold = rating_threshold
            self.preferences = preferences
            self.visited_restaurant = visited_restaurant
            self.limit = os.getenv("DEFAULT_LIMIT")
            self.query = RestaurantQuerySchema(travel_radius=self.radius, rating_threshold=self.rating_threshold, restaurant_types=self.preferences, visited_restaurants=self.visited_restaurant, result_limit=self.limit).getQuerySchemeBasedOnCurrentCoordinates(latitude=lat, longitude=long)
        else:   
            self.current_location = current_location
            self.radius = radius
            self.rating_threshold = rating_threshold
            self.preferences = preferences
            self.visited_restaurant = visited_restaurant
            self.limit = os.getenv("DEFAULT_LIMIT")
            self.query = RestaurantQuerySchema(current_location=self.current_location,travel_radius=self.radius, rating_threshold=self.rating_threshold, restaurant_types=self.preferences, visited_restaurants=self.visited_restaurant, result_limit=self.limit).getQuerySchema()
        
    def getRestaurants(self):
        print("Geting Restaurants", os.getenv("SPARQL_ENDPOINT"))
        self.sparql = SPARQLService(sparql_endpoint=os.getenv("SPARQL_ENDPOINT"), username=os.getenv("USERNAME"), password=os.getenv("PASSWORD")).getSparqlWrapper()
        self.sparql.setQuery(self.query)
        print("Query is",self.query)
        restaurant_data = []
        try:
            print("SPARQL", self.sparql.query())

            results = self.sparql.query().convert()
            print("Results", results)
            for result in results["results"]["bindings"]:
                restaurant_info = {
                    "Restaurant": result['restaurant']['value'],
                    "name": result['name']['value'],
                    "Type": result['type']['value'],
                    'distance': result['distance']['value'],
                    "Address": result['address']['value'],
                    "rating": result['rating']['value'],
                    "Geom": result['geom']['value']
                }
                restaurant_data.append(restaurant_info)
            return restaurant_data    
        except Exception as e:
            (f"An error occurred: {e}")
            return []    
           





