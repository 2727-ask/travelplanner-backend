from SPARQLWrapper import SPARQLWrapper, JSON

class SPARQLService:
    _instance = None  # Class-level variable to hold the singleton instance

    def __new__(cls, sparql_endpoint, username=None, password=None):
        if cls._instance is None:
            cls._instance = super(SPARQLService, cls).__new__(cls)
            cls._instance.sparql_endpoint = sparql_endpoint
            cls._instance.sparql_wrapper = SPARQLWrapper(sparql_endpoint)
            if username and password:
                cls._instance.sparql_wrapper.setCredentials(username, password)    
        return cls._instance

    def getSparqlWrapper(self):
        self.sparql_wrapper.setReturnFormat(JSON)
        self.sparql_wrapper.addCustomParameter('Accept', 'application/json')
        return self.sparql_wrapper
    

    
    



    


