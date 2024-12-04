from services.restaurantService import RestaurantService
from services.pointOfInterestService import PointOfInterestService
from datetime import datetime, timedelta
from models.VehicleEnum import Vehicle
import os

class IternaryService:
    def __init__(self, vehicle, travelTime, radius, rating_threshold, preferences, interests=[], current_timestamp='7:00'):
        self.interests = interests
        self.vehicle = vehicle
        self.travelTime = travelTime
        self.radius = radius
        self.rating_threshold = rating_threshold
        self.preferences = preferences
        self.visited_restaurant = []
        # Convert environment variable to float (assuming it's in hours)
        self.default_restaurant_wait_time = float(os.getenv("DEFAULT_RESTAURANT_WAITTIME", 1))  # Default to 1 hour if not set
        self.currentStateTimeStamp =  current_timestamp
        self.itenary = []
        self.places_by_time = {
            "morning": ["Park", "Trail", "Lake", "Church", "Valley"],
            "afternoon": ["Museum", "Park", "Beach", "Harbor"],
            "evening": ["Summit", "Dam", "Lake", "Church", "Park", "Valley"],
            "night": ["Island", "Waterfall", "Beach"]
        }   
        self.time_buffer=float(os.getenv("TIME_BUFFER"))
        self.default_poi_wait_time = float(os.getenv("DEFAULT_DESINATION_WAITTIME", 3))


    def find_best_restaurant(self, restaurants):
        # Convert all ratings to floats and distances to floats
        for restaurant in restaurants:
            restaurant['rating'] = float(restaurant['rating'])
            restaurant['distance'] = float(restaurant['distance'])
        
        # Sort restaurants first by Rating (descending), then by Distance (ascending)
        best_restaurant = sorted(restaurants, key=lambda x: (-x['rating'], x['distance']))[0]
        
        return best_restaurant    

    def calculateTimeToReachDestination(self, distance):
        if(self.vehicle == Vehicle.CAR):
            speed = 30000  # meters/hr
            time = float(distance) / speed  # hours
            return time  # hours
        # Todo for other vehicles
        return 0

        
    def getCurrentRestaurantBasedOnCoordinates(self, latitude, longitude):
            self.destination = None
            
            # Get the current food interval based on the current state time
            current_interval = self.get_food_interval(self.currentStateTimeStamp)
            #print(f"Current Food Interval: {current_interval}")

            # Combine the current interval and preferences for restaurant search
            preference = [current_interval]
            for p in self.preferences:
                preference.append(p)
            #print(f"Preferences: {preference}")

            # Instantiate the RestaurantService to fetch the list of restaurants
            resService = RestaurantService(
                lat=latitude,
                long=longitude, 
                radius=self.radius, 
                rating_threshold=self.rating_threshold, 
                preferences=preference, 
                visited_restaurant=self.visited_restaurant
            )
            
            # Get the best restaurant from the list
            destination = self.find_best_restaurant(resService.getRestaurants())
            #print(f"Best Restaurant Found: {destination}")

            # Add restaurant wait time and travel time to the current state timestamp
            new_time = datetime.strptime(self.currentStateTimeStamp, "%H:%M") + \
                    timedelta(hours=self.default_restaurant_wait_time) + \
                    timedelta(hours=self.calculateTimeToReachDestination(destination['distance']), minutes=self.time_buffer)

            
            # Convert the new time back to the "HH:MM" string format
            self.currentStateTimeStamp = new_time.strftime("%H:%M")
            #print(f"TIME_NOW: {self.currentStateTimeStamp}")

            # Update the remaining travel time
            self.travelTime -= self.default_restaurant_wait_time + self.calculateTimeToReachDestination(destination['distance'])
            #print(f"Remaining Travel Time: {self.travelTime} hours")

            # Update the current location after visiting the restaurant
            self.current_location = destination.get('Restaurant').split('itp#')[1]
            #print(f"Updated Current Location: {self.current_location}")

            self.visited_restaurant.append(self.current_location)

            destination['Current Food Interval'] = current_interval
            destination['Preferences'] = self.preferences
            destination['TIME_NOW'] = self.currentStateTimeStamp
            destination['Remaining Travel Time'] = self.travelTime
            destination['Updated Current Location'] = self.current_location
            destination['TimeToReachDestination'] = self.calculateTimeToReachDestination(destination['distance']) + self.time_buffer


            # Return the best restaurant
            return destination
        
    def find_closest_destination(self, destinations):
        closest = None
        closest_distance = float('inf')  # Set the initial closest distance to infinity

        for destination in destinations:
            # Extract the distance and convert it to a float
            distance = float(destination['distance'])

            # Check if the current destination has a smaller distance
            if distance < closest_distance:
                closest_distance = distance
                closest = destination

        return closest    
    
    def getPOI(self, latitude, longitude, interest, visited_places):
        poiService = PointOfInterestService(lat=latitude, long=longitude, radius=self.radius, preferences=interest, visited_places=visited_places)
        destination = self.find_closest_destination(poiService.getDestination())
        new_time = datetime.strptime(self.currentStateTimeStamp, "%H:%M") + \
                    timedelta(hours=self.default_poi_wait_time) + \
                    timedelta(hours=self.calculateTimeToReachDestination(destination['distance']))
            
            # Convert the new time back to the "HH:MM" string format
        self.currentStateTimeStamp = new_time.strftime("%H:%M")
        destination['TIME_NOW'] = self.currentStateTimeStamp
        destination['TimeToReachDestination'] = self.calculateTimeToReachDestination(destination['distance']) + self.time_buffer

        return destination

    def get_food_interval(self, time_stamp):
        # Convert the time_stamp to a datetime object
        time = datetime.strptime(time_stamp, "%H:%M")
        
        # Define time ranges for each food interval
        breakfast_start = datetime.strptime("06:00", "%H:%M")
        breakfast_end = datetime.strptime("09:00", "%H:%M")
        
        brunch_start = datetime.strptime("09:01", "%H:%M")
        brunch_end = datetime.strptime("11:00", "%H:%M")
        
        lunch_start = datetime.strptime("11:01", "%H:%M")
        lunch_end = datetime.strptime("14:00", "%H:%M")
        
        afternoon_tea_start = datetime.strptime("14:01", "%H:%M")
        afternoon_tea_end = datetime.strptime("16:00", "%H:%M")
        
        dinner_start = datetime.strptime("16:01", "%H:%M")
        dinner_end = datetime.strptime("20:00", "%H:%M")
        
        dessert_start = datetime.strptime("20:01", "%H:%M")
        dessert_end = datetime.strptime("23:59", "%H:%M")
        
        # Check which food interval applies
        if breakfast_start <= time <= breakfast_end:
            return "Breakfast"
        elif brunch_start <= time <= brunch_end:
            return "Brunch"
        elif lunch_start <= time <= lunch_end:
            return "Lunch"
        elif afternoon_tea_start <= time <= afternoon_tea_end:
            return "Afternoon Tea"
        elif dinner_start <= time <= dinner_end:
            return "Dinner"
        elif dessert_start <= time <= dessert_end:
            return "Dessert"
        else:
            return None
        

    def get_time_period(self,time_str):
        """Returns the appropriate time period based on the input time."""
        time = datetime.strptime(time_str, "%H:%M").time()

        if datetime.strptime("06:00", "%H:%M").time() <= time <= datetime.strptime("09:00", "%H:%M").time():
            return "morning"
        elif datetime.strptime("09:01", "%H:%M").time() <= time <= datetime.strptime("11:00", "%H:%M").time():
            return "mid_morning"
        elif datetime.strptime("11:01", "%H:%M").time() <= time <= datetime.strptime("14:00", "%H:%M").time():
            return "early_afternoon"
        elif datetime.strptime("14:01", "%H:%M").time() <= time <= datetime.strptime("16:00", "%H:%M").time():
            return "afternoon"
        elif datetime.strptime("16:01", "%H:%M").time() <= time <= datetime.strptime("20:00", "%H:%M").time():
            return "evening"
        elif datetime.strptime("20:01", "%H:%M").time() <= time <= datetime.strptime("23:59", "%H:%M").time():
            return "night"
        else:
            return "night"  
           

    def suggest_places(self, time_str):
        """Returns suggested places based on the input time."""
        period = self.get_time_period(time_str)
        return self.places_by_time.get(period, []) 
    




      
