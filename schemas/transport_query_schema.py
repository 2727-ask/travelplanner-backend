class TransportQuerySchema:
    def __init__(self, current_location=None, travel_radius=None, rating_threshold=None, Transport_types=None, visited_Transports=None, result_limit=None):
        self.current_location = current_location
        self.travel_radius = travel_radius
        self.rating_threshold = rating_threshold
        self.Transport_types = Transport_types  # List of types to include in the query
        self.visited_Transports = visited_Transports
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
        SELECT ?Transport ?name ?type ?distance ?address ?rating ?geom
        WHERE {{
            # Retrieve the geometry of the current location
            itp:{self.current_location} geo:hasGeometry ?currentGeom .
            ?currentGeom geo:asWKT ?currentWKT .
            
            # Find Transport
            ?Transport a geo:Feature ;
                        geo:hasGeometry ?geom ;
                        itp:hasTransportName ?name ;
                        itp:hasAddressTransport ?address ;
                        itp:isTransportOpen ?isOpen ;
                        itp:hasRatingTransport ?rating ;
                        itp:hasTransportCategories ?type .
            
            # Ensure the place is Open
            FILTER(?isOpen = 1)
            
            # Ensure the place has a rating greater than the threshold
            FILTER(?rating > {self.rating_threshold})
            
            # Retrieve the geometry of the Transports
            ?geom geo:asWKT ?TransportWKT .
            
            # Calculate the distance
            BIND(geof:distance(?currentWKT, ?TransportWKT, units:metre) AS ?distance)
            
            # Filter by distance
            FILTER(?distance < {self.travel_radius})
        """
        
        # Add dynamic filters for Transport types
        if self.Transport_types:
            type_filters = " || ".join(
                [f"CONTAINS(?type, \"{Transport_type}\")" for Transport_type in self.Transport_types]
            )
            base_query += f"\n            FILTER({type_filters})"

        # Add dynamic filters for visited Transports
        if self.visited_Transports:
            exclusion_filters = "\n".join(
                [f"FILTER(?Transport != itp:{Transport})" for Transport in self.visited_Transports]
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
        SELECT ?Transport ?name ?type ?distance ?address ?rating ?geom
        WHERE {{
            # Bind dynamic coordinates as WKT geometry
            BIND(STRDT(CONCAT("POINT(", STR({longitude}), " ", STR({latitude}), ")"), geo:wktLiteral) AS ?currentWKT)
            
            # Find Transports
            ?Transport a geo:Feature ;
                        geo:hasGeometry ?geom ;
                        itp:hasTransportName ?name ;
                        itp:hasAddressTransport ?address ;
                        itp:isTransportOpen ?isOpen ;
                        itp:hasRatingTransport ?rating ;
                        itp:hasTransportCategories ?type .
            
            # Ensure the place is open
            FILTER(?isOpen = 1)
            
            # Ensure the Transport rating is greater than the threshold
            FILTER(?rating > {self.rating_threshold})
            
            # Retrieve the geometry of the Transports
            ?geom geo:asWKT ?TransportWKT .
            
            # Calculate the distance
            BIND(geof:distance(?currentWKT, ?TransportWKT, units:metre) AS ?distance)
            
            # Filter by distance
            FILTER(?distance < {self.travel_radius})
        """
        
        # Add dynamic filters for Transport types
        if self.Transport_types:
            type_filters = " || ".join(
                [f"CONTAINS(?type, \"{Transport_type}\")" for Transport_type in self.Transport_types]
            )
            base_query += f"\n            FILTER({type_filters})"

        # Add dynamic filters for visited Transports
        if self.visited_Transports:
            exclusion_filters = "\n".join(
                [f"FILTER(?Transport != itp:{Transport})" for Transport in self.visited_Transports]
            )
            base_query += f"\n            {exclusion_filters}"

        # Close the query
        base_query += f"""
        }}
        ORDER BY ?distance
        LIMIT {self.result_limit}
        """
        return prefixes + base_query




# schema = TransportQuerySchema(
#     current_location="Red_Mango_420_S_Mill_Ave_Ste_107",
#     travel_radius=4000,
#     rating_threshold=3,
#     Transport_types=["Veg", "Chinese"],
#     visited_Transports=["Little_Szechuan_524_W_University_Dr", "Asian_Fusion_Cafe_725_S_Rural_Rd_Ste_103"],
#     result_limit=10
# )

# query = schema.getQuerySchema()
# print(query)
