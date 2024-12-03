class POIQuerySchema:
    def __init__(self, latitude, longitude, travel_radius, name_or_type_keywords, result_limit, visited_places):
        self.latitude = latitude
        self.longitude = longitude
        self.travel_radius = travel_radius
        self.name_or_type_keywords = name_or_type_keywords  # List of keywords to match in name or type
        self.result_limit = result_limit
        self.visited_places = visited_places

    def getQuerySchema(self):
        prefixes = """
        PREFIX geo: <http://www.opengis.net/ont/geosparql#>
        PREFIX geof: <http://www.opengis.net/def/function/geosparql/>
        PREFIX units: <http://www.opengis.net/def/uom/OGC/1.0/>
        PREFIX itp: <http://www.semanticweb.org/team11/ontologies/2024/10/itp#>
        PREFIX gnis: <http://gnis-ld.org/lod/gnis/ontology/>
        """

        # Generate FILTER clauses for matching name or type using CONTAINS
        filter_conditions = " || ".join(
            [f'CONTAINS(LCASE(STR(?name)), LCASE("{keyword}")) || CONTAINS(LCASE(STR(?type)), LCASE("{keyword}"))' 
             for keyword in self.name_or_type_keywords]
        )

        # Visited POIs exclusion using MINUS
        visited_places_triples = "\n".join(
            f'    <{poi}> a geo:Feature .' for poi in self.visited_places
        )

        base_query = f"""
        SELECT ?POI ?name ?distance ?type ?county ?state ?geom
        WHERE {{
            BIND(STRDT(CONCAT("POINT(", STR({self.longitude}), " ", STR({self.latitude}), ")"), geo:wktLiteral) AS ?currentWKT)
            
            ?POI a geo:Feature ;
                 geo:hasGeometry ?geom ;
                 itp:hasFeatureName ?name ;
                 itp:hasPOIClass ?type ;
                 itp:inState ?state ;
                 itp:inCounty ?county .
                 
            ?geom geo:asWKT ?POIWKT .
            
            BIND(geof:distance(?currentWKT, ?POIWKT, units:metre) AS ?distance)
            
            FILTER(?distance < {self.travel_radius})
            FILTER({filter_conditions})
            
            MINUS {{
                {visited_places_triples}
            }}
        }}
        ORDER BY ?distance
        LIMIT {self.result_limit}
        """
        return prefixes + base_query


# Example usage:
schema = POIQuerySchema(
    latitude=33.424564,
    longitude=-111.928001,
    travel_radius=4000,
    name_or_type_keywords=["museum", "park", "historic"],  # Keywords to search in name or type
    result_limit=10,
    visited_places=[
        "http://www.semanticweb.org/team11/ontologies/2024/10/itp#Tempe_Butte_Tempe_12234",
        "http://www.semanticweb.org/team11/ontologies/2024/10/itp#Tempe_Shopping_Center_Tempe_15113"
    ]
)

query = schema.getQuerySchema()
print(query)
