class RestaurantQuerySchema:
    def __init__(self, current_location=None, travel_radius=None, rating_threshold=None, restaurant_types=None, visited_restaurants=None, result_limit=None):
        self.current_location = current_location
        self.travel_radius = travel_radius
        self.rating_threshold = rating_threshold
        self.restaurant_types = restaurant_types  # List of types to include in the query
        self.visited_restaurants = visited_restaurants
        self.result_limit = result_limit

    def getQuerySchema(self):
        prefixes = """
        PREFIX geo: <http://www.opengis.net/ont/geosparql#>
        PREFIX geof: <http://www.opengis.net/def/function/geosparql/>
        PREFIX units: <http://www.opengis.net/def/uom/OGC/1.0/>
        PREFIX ex: <http://example.org/>
        PREFIX itp: <http://www.semanticweb.org/team11/ontologies/2024/10/itp#>
        """
        base_query = f"""
        SELECT ?restaurant ?name ?type ?distance ?address ?rating ?geom
        WHERE {{
            # Retrieve the geometry of the current location
            itp:{self.current_location} geo:hasGeometry ?currentGeom .
            ?currentGeom geo:asWKT ?currentWKT .
            
            # Find Restaurant
            ?restaurant a geo:Feature ;
                        geo:hasGeometry ?geom ;
                        itp:hasRestaurantName ?name ;
                        itp:hasAddressRestaurant ?address ;
                        itp:isRestaurantOpen ?isOpen ;
                        itp:hasRatingRestaurant ?rating ;
                        itp:hasRestaurantCategories ?type .
            
            # Ensure the place is Open
            FILTER(?isOpen = 1)
            
            # Ensure the place has a rating greater than the threshold
            FILTER(?rating > {self.rating_threshold})
            
            # Retrieve the geometry of the restaurants
            ?geom geo:asWKT ?restaurantWKT .
            
            # Calculate the distance
            BIND(geof:distance(?currentWKT, ?restaurantWKT, units:metre) AS ?distance)
            
            # Filter by distance
            FILTER(?distance < {self.travel_radius})
        """
        
        # Add dynamic filters for restaurant types
        if self.restaurant_types:
            type_filters = " || ".join(
                [f"CONTAINS(?type, \"{restaurant_type}\")" for restaurant_type in self.restaurant_types]
            )
            base_query += f"\n            FILTER({type_filters})"

        # Add dynamic filters for visited restaurants
        if self.visited_restaurants:
            exclusion_filters = "\n".join(
                [f"FILTER(?restaurant != itp:{restaurant})" for restaurant in self.visited_restaurants]
            )
            base_query += f"\n            {exclusion_filters}"

        # Close the query
        base_query += f"""
        }}
        ORDER BY ?distance
        LIMIT {self.result_limit}
        """

        return prefixes + base_query
    
    def getQuerySchemeBasedOnCurrentCoordinates(self, latitude, longitude):
        prefixes = """
        PREFIX geo: <http://www.opengis.net/ont/geosparql#>
        PREFIX geof: <http://www.opengis.net/def/function/geosparql/>
        PREFIX units: <http://www.opengis.net/def/uom/OGC/1.0/>
        PREFIX itp: <http://www.semanticweb.org/team11/ontologies/2024/10/itp#>
        """
        
        # Bind dynamic latitude and longitude
        base_query = f"""
        SELECT ?restaurant ?name ?type ?distance ?address ?rating ?geom
        WHERE {{
            # Bind dynamic coordinates as WKT geometry
            BIND(STRDT(CONCAT("POINT(", STR({longitude}), " ", STR({latitude}), ")"), geo:wktLiteral) AS ?currentWKT)
            
            # Find Restaurants
            ?restaurant a geo:Feature ;
                        geo:hasGeometry ?geom ;
                        itp:hasRestaurantName ?name ;
                        itp:hasAddressRestaurant ?address ;
                        itp:isRestaurantOpen ?isOpen ;
                        itp:hasRatingRestaurant ?rating ;
                        itp:hasRestaurantCategories ?type .
            
            # Ensure the place is open
            FILTER(?isOpen = 1)
            
            # Ensure the restaurant rating is greater than the threshold
            FILTER(?rating > {self.rating_threshold})
            
            # Retrieve the geometry of the restaurants
            ?geom geo:asWKT ?restaurantWKT .
            
            # Calculate the distance
            BIND(geof:distance(?currentWKT, ?restaurantWKT, units:metre) AS ?distance)
            
            # Filter by distance
            FILTER(?distance < {self.travel_radius})
        """
        
        # Add dynamic filters for restaurant types
        if self.restaurant_types:
            type_filters = " || ".join(
                [f"CONTAINS(?type, \"{restaurant_type}\")" for restaurant_type in self.restaurant_types]
            )
            base_query += f"\n            FILTER({type_filters})"

        # Add dynamic filters for visited restaurants
        if self.visited_restaurants:
            exclusion_filters = "\n".join(
                [f"FILTER(?restaurant != itp:{restaurant})" for restaurant in self.visited_restaurants]
            )
            base_query += f"\n            {exclusion_filters}"

        # Close the query
        base_query += f"""
        }}
        ORDER BY ?distance
        LIMIT {self.result_limit}
        """
        return prefixes + base_query




# schema = RestaurantQuerySchema(
#     current_location="Red_Mango_420_S_Mill_Ave_Ste_107",
#     travel_radius=4000,
#     rating_threshold=3,
#     restaurant_types=["Veg", "Chinese"],
#     visited_restaurants=["Little_Szechuan_524_W_University_Dr", "Asian_Fusion_Cafe_725_S_Rural_Rd_Ste_103"],
#     result_limit=10
# )

# query = schema.getQuerySchema()
# print(query)
