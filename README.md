To solve this problem, we need to optimize the delivery of orders from the warehouse in Cincinnati, OH, using the available trucks and drivers. The goal is to minimize the overall cost, which includes factors like driver salaries, fuel consumption, and truck capacity utilization.

Understanding the Data

1.	item_info.csv:
 
Contains details about items, including:
  o	ItemId: Unique identifier for each item.
  o	weight (pounds): Weight of each item.
  o	warehouse origin: All items originate from Cincinnati, OH.

2.	orders.csv:

Contains details about orders, including:
  o	Company: The customer.
  o	Item: The item ID.
  o	Number of Units: The quantity of the item ordered.
  o	Destination: The city and state for delivery.
  o	There are two unnamed columns that appear to be empty.

3.	trucks.xlsx (Sheet1):

Contains details about available trucks and drivers:
  o	Truck ID: Unique truck identifier.
  o	Driver Name: Assigned driver.
  o	Years Experience: Experience level of the driver.
  o	Truck Type (length in m): The truck size.
  o	Weight Capacity (kg): The maximum weight capacity.
  o	Top Speed (km/h): The truck’s speed.
  o	Driver Hourly Rate: The cost per hour for the driver.
  o	Fuel Tank Size (gallon): The fuel tank capacity.
  o	Spare Tires: Number of spare tires available.
  o	Truck Age (years): The age of the truck.

Next Steps

1.	Optimization Approach:
  o	Assign orders to trucks based on weight capacity.
  o	Group orders by location to minimize route costs.
  o	Plan truck routes to visit multiple locations efficiently.
  o	Consider driver working limits (14-hour shifts, 10-hour breaks).
  o	Minimize fuel and labour costs.

2.	Python Implementation:
  o	API to accept orders and return optimized delivery plans.
  o	Route optimization using Google OR-Tools or Graph Algorithms.
  o	Cost estimation based on fuel and driver wages.

3.	Deployment on Azure:
  o	API deployed using Azure App Service.
  o	Azure Functions for automated scheduling.
  o	Azure Cosmos DB for storing order and route data.
  o	Azure Machine Learning for cost predictions (optional).
  o	Docker for containerized deployment.

4.	Infrastructure Configuration:
  o	YAML file for Azure services.
  o	Dockerfile for containerized API deployment.

Assumptions
  •	All trucks start and end their journey at the Cincinnati warehouse.
  •	Fuel consumption is directly proportional to distance travelled.
  •	Driver costs are based on the time taken to complete the route.
  •	The road network and distances between cities are known and can be used for route planning.


