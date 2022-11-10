# Case Study
## Store Returns Optimization

This code helped a returns logistics company analyze a new business process proposal, given two pieces of data:
1. List of stores - store ids, and number of returns per store per day, city location
2. City information - city name, state, latitude, longitude

The goal was to create a clusters in each state, with the following constraints:
1. Each cluster should be optimized to minimize the distance traveled by the driver
2. Each cluster should have at least 70 returns per day
3. Clusters should not have stores from different states

The optimization is achieved by applying the traveling salesman problem (TSP) to each cluster to find the optimal route for the driver. The TSP is solved using the mlrose library.

## Notes
- The code will not run because it is missing the data files. The data files are not included in this repository because they are proprietary.

## Todo:
1. Add sample data files
2. Create visualization of the clusters