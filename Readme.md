# Case Study
## Store Returns Optimization

This code helped a returns logistics company analyze a new business proposal. It needed to define clusters of stores that in aggregate had returns greater than a certain threshold and minimize the miles driven to collect all of the returns for the stores in the cluster.

Data Given
1. List of stores - store ids, and number of returns per store per day, city location
2. City information - city name, state, latitude, longitude

The goal was to create a clusters in each state, with the following constraints:
1. Each cluster should have at least `X` returns per day
2. Clusters should not have stores from different states
3. Total miles driven per cluster should be less than `Y` miles to minimize the distance traveled by the driver

The optimization is achieved by applying the traveling salesman problem (TSP) to each cluster to find the optimal route for the driver. The TSP is solved using the mlrose library.

The Solver starts by finding the "primary store" or stores with the most returns that is availabe. It then creates a cluster and puts store in the cluster. It then goes on to find then analyzes the possible routes/return combinations of the nearby store and add the best routes/stores to the cluster. The solver will continue this process until there are no more satisfactory options.

##### Current process takes about 5 minutes to run with the sample data provided.

## Possible Improvements:
- Visualization of stores, cluster, and routes
- Optimze algorithm for performance