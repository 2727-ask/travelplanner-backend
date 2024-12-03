http://localhost:7200/sparql?name=Unnamed&query=PREFIX%20geo%3A%20%3Chttp%3A%2F%2Fwww.opengis.net%2Font%2Fgeosparql%23%3E%0APREFIX%20geof%3A%20%3Chttp%3A%2F%2Fwww.opengis.net%2Fdef%2Ffunction%2Fgeosparql%2F%3E%0APREFIX%20units%3A%20%3Chttp%3A%2F%2Fwww.opengis.net%2Fdef%2Fuom%2FOGC%2F1.0%2F%3E%0APREFIX%20ex%3A%20%3Chttp%3A%2F%2Fexample.org%2F%3E%0APREFIX%20itp%3A%20%3Chttp%3A%2F%2Fwww.semanticweb.org%2Fteam11%2Fontologies%2F2024%2F10%2Fitp%23%3E%0ASELECT%20%3Frestaurant%20%3Fname%20%3Ftype%20%3Fdistance%20%3Faddress%20%3Frating%0AWHERE%20%7B%0A%20%20%20%20%23%20Retrieve%20the%20geometry%20of%20the%20current%20location%20()%0A%20%20%20%20itp%3ARed_Mango_420_S_Mill_Ave_Ste_107%20geo%3AhasGeometry%20%3FcurrentGeom%20.%0A%20%20%20%20%3FcurrentGeom%20geo%3AasWKT%20%3FcurrentWKT%20.%0A%20%20%20%20%23%20Find%20Restaurant%0A%20%20%20%20%3Frestaurant%20a%20geo%3AFeature%20%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20geo%3AhasGeometry%20%3Fgeom%20%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20itp%3AhasRestaurantName%20%3Fname%20%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20itp%3AhasAddressRestaurant%20%3Faddress%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20itp%3AisRestaurantOpen%20%3FisOpen%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20itp%3AhasRatingRestaurant%20%3Frating%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20itp%3AhasRestaurantCategories%20%3Ftype%20.%0A%20%20%20%20%23%20Ensure%20the%20place%20is%20Open%0A%20%20%20%20FILTER(%3FisOpen%3D1)%0A%20%20%20%20%23%20Ensure%20the%20place%20has%20greater%20than%203%20rating%0A%20%20%20%20FILTER(%3Frating%3E3)%0A%20%20%20%20%23%20Ensure%20the%20place%20type%20is%20a%20chinese%20Restaurant%0A%20%20%20%20FILTER(CONTAINS(%3Ftype%2C%20%22Chinese%22))%0A%20%20%20%20%23%20Retrieve%20the%20geometry%20of%20the%20restaurants%0A%20%20%20%20%3Fgeom%20geo%3AasWKT%20%3FrestaurantWKT%20.%0A%20%20%20%20%23%20Calculate%20the%20distance%0A%20%20%20%20BIND(geof%3Adistance(%3FcurrentWKT%2C%20%3FrestaurantWKT%2C%20units%3Ametre)%20AS%20%3Fdistance)%0A%20%20%20%20%23%20Filter%20by%20distance%20(4%20km%20%3D%2040%2C00%20meters)%0A%20%20%20%20FILTER(%3Fdistance%20%3C%204000)%0A%7D%0AORDER%20BY%20%3Fdistance%0ALIMIT%2010&infer=true&sameAs=true





TODO: 

1] SETUP FAST API APPLICATION
2] CREATE CONSTANTS FOR AVERAGE SPENT TIME AT A PLACE
3] FETCH CURRENT LOCATION OF THE USER [for now it is phoenix airport]
4] GET USER INTEREST
5] MAINTAIN A DATA STRUCTURE TO STORE ALREADY VISITED PLACES
6] GET THE TRAVELLING DATES, AND DAYS TO TRAVEL. [default 1 day which is 8 hour journey] TOTAL_TIME_AVAILABLE = 8;
7] CHECK TRAVEL START TIME. [FOR NOW WE WILL KEEP IT AS 9:00 AM]
8] LETS ASSUME THE USER HAS A CAR AND AVERAGE TRAVEL SPEED IS 45 KM/HR
9] FIRST WE WILL SUGGEST HIM RESTAURANTS FOR BREAKFAST WITHIN 5 KM OF RANGE. CALCULATE THE TOTAL TRAVEL TIME REQUIRED USING SPEED FORMULA.
QUERY THE BEST PLACE FOR USER AND UPDATE THE DATA STRUCTURE. SUBTRACT 1.5 + TRAVEL TIME HOUR FROM THE TIME AVAILABLE
10] THEN SUGGEST INTERESTING PLACE FROM THERE AND FIND OUT BEST PLACE FROM THE RESTAURANT, CALCULATE TOTAL TRAVEL TIME AND SPEND TIME. DEDUCT THE TOTAL TIME AVAILABLE
11] DO THIS PROCESS REPEATATIVELY.



POI SERVICE:

1] Create POI Query Scheme
2] FETCH USER INTERESTS
3] FIND TYPES OF TRAVEL ITENARY
4] FIND THE BEST SCHEDULES
5] CREATE TEMPLATES



A] Day Planner
1] Fetch Day Iternary Templates
2] Iterate through iternary
3] Find the best match
4] If best match not found go to the interests and show location






1] Morning BreakFast
2] Place
3] Brunch
4] Place
5] Lunch
6] Relax Place
7] Snacks
8] Place
9] Dinner
10] Dessert

Museum
Lake
Beach
Waterfall
Church
Summit (Mountain Trek)
Trail (Hiking Trail)
Park
Harbor
Dam
Island
Valley
Garden



INPUTS:
1] Trek, Garden, Shopping, Museum
2] Veg, Italian



Day planner: 16 hrs Day starts at 7 am
1] **Breakfast 1hr
2] **Place (if Trek interest suggest it). 3hr
3] Afternoon Lunch 1hr
4] **Place (No trek) 3hr
5] Evening Snacks 1hr
6] **Place (No trek) 3hr
7] Dinner 1hr





Notes:
1] Work on feedback loop



Lake
Beach
Waterfall
Airport
Church
Summit (Mountain Trek)
Trail (Hiking Trail)
Park
Harbor
Hospital
Dam
Island
Valley

Summit/Trail
Valley
Church
Museum
Park
Shopping
Garden
Lake


Do Breakfast
calc time
Go to Place




