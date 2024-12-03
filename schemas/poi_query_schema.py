class POIQuerySchema:
    def __init__(self, latitude, longitude, travel_radius, feature_types, result_limit, visited_places=[]):
        self.latitude = latitude
        self.longitude = longitude
        self.travel_radius = travel_radius
        self.feature_types = feature_types  # Accepts a list of feature types
        self.result_limit = result_limit
        self.visited_places = visited_places  # Accepts a list of visited places as string URIs

    def getQuerySchema(self):
        prefixes = """
        PREFIX geo: <http://www.opengis.net/ont/geosparql#>
        PREFIX geof: <http://www.opengis.net/def/function/geosparql/>
        PREFIX units: <http://www.opengis.net/def/uom/OGC/1.0/>
        PREFIX itp: <http://www.semanticweb.org/team11/ontologies/2024/10/itp#>
        """
        
        # Dynamic feature filter creation
        feature_filters = " || ".join(
            [f'CONTAINS(?type, "{feature}") || CONTAINS(?name, "{feature}")' for feature in self.feature_types]
        )

        # Dynamic visited places filter creation
        visited_filter = ""
        if self.visited_places:
            visited_uris = " ".join([f'FILTER(?POI != {uri})' for uri in self.visited_places])
            visited_filter = visited_uris

        query = f"""
        SELECT ?POI ?name ?distance ?type ?county ?state ?geom
        WHERE {{
            # Bind dynamic coordinates as WKT geometry
            BIND(STRDT(CONCAT("POINT(", STR({self.longitude}), " ", STR({self.latitude}), ")"), geo:wktLiteral) AS ?currentWKT)
            
            # Find POIs (Points of Interest)
            ?POI a geo:Feature ;
                 geo:hasGeometry ?geom ;
                 itp:hasFeatureName ?name ;
                 itp:hasPOIClass ?type ;
                 itp:inState ?state ;
                 itp:inCounty ?county .
            
            # Retrieve the geometry of the POIs
            ?geom geo:asWKT ?POIWKT .
            
            # Calculate the distance of the POIs
           
            
            # Filter by feature types and distance
            FILTER(({feature_filters}) && ?distance < {self.travel_radius})
            
            # Exclude visited places
            {visited_filter}

            BIND(geof:distance(?currentWKT, ?POIWKT, units:metre) AS ?distance)
        }}
        ORDER BY ?distance
        LIMIT {self.result_limit}
        """
        
        return prefixes + query
