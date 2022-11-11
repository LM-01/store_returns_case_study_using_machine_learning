from utils import re_arrange_path
import math
import six
import sys
sys.modules['sklearn.externals.six'] = six
import mlrose

class Cluster:
    def __init__(self, cluster_id):
        self.state = None
        self.primary = None
        self.satelite_stores = []
        self.all_stores_in_cluster = []
        self.cluster_returns = 0
        self.cluster_id = cluster_id
        self.miles_to_sweep = 0
        self.max_distance = 60
        self.cluster_connections = None
        self.store_cluster_id = 0
        self.optimal_path = {}
        self.path = []
        
    def assign_store_cluster_id(self):
        for i,store in enumerate(self.all_stores_in_cluster):
            store.store_cluster_id = i

    def add_primary(self, store):
        #print(f'Adding Primary: {store.store_number}')
        store.paired = True
        store.store_cluster_id = self.assign_store_cluster_id()
        self.cluster_returns += store.returns
        self.primary = store
        store.distance_to_primary = 0
        self.all_stores_in_cluster.append(store)
        
    
    def add_store(self, store):
        if store.paired == True:
            raise Exception("Cannot add a paired store to a cluster")
        if math.isnan(store.lat) or math.isnan(store.lng):
            store.rejected = True
            print(f'Did not add store {store.store_number} due to bad coordinates.')
        else:
            store.paired = True
            store.store_cluster_id = self.assign_store_cluster_id()
            self.cluster_returns += store.returns
            self.satelite_stores.append(store)
            self.all_stores_in_cluster.append(store)
            #print(f'Adding store: {store.store_number} - Cluster Returns: {self.cluster_returns}')
    
    def remove_store(self, store):
        # Removes the store from the cluster and makes it available again
        store.paired = False
        store.store_cluster_id = None
        self.cluster_returns -= store.returns
        self.satelite_stores = [storex for storex in self.satelite_stores if storex != store]
        self.all_stores_in_cluster = [self.primary] + self.satelite_stores

    def remove_last_store_added(self):
        # Removes the last store added to the cluster
        store = self.all_stores_in_cluster.pop()
        self.remove_store(store)
    
    def calc_miles_to_sweep(self):
        #Adds the miles from the primary store to all the satellite stores
        miles = 0
        for store in self.satelite_stores:
            miles += store.calc_distance_to_other_store(self.primary)
        self.miles_to_sweep = miles
        return miles

    def calc_cluster_store_distances(self):
        # Returns the distance between each of the stores in the cluster stores list
        self.assign_store_cluster_id()
        distances = []
        for i,store in enumerate(self.all_stores_in_cluster):
            for j, next_store in enumerate(self.all_stores_in_cluster):
                dist = store.calc_distance_to_other_store(next_store)
                if i == j:
                    pass
                else:
                    distances.append((store.store_cluster_id, next_store.store_cluster_id, dist))
        return distances
    
    
    def get_optimial_path(self):
        # Calculate the best optimal route for each cluster, and appends it to the "optimal_path" attributes
        # returns the best_fitness aka number of miles of the path
        routes = self.calc_cluster_store_distances()
        print(f'Getting optimal route for: {self.state} {routes}')
        if len(routes) > 1:
          self.cluster_connections = routes
          fitness_dists = mlrose.TravellingSales(distances = routes)
          problem_fit = mlrose.TSPOpt(length = len(self.all_stores_in_cluster), fitness_fn = fitness_dists,
                            maximize=False)
          # Solve problem using the genetic algorithm
          best_state, best_fitness = mlrose.genetic_alg(problem_fit, mutation_prob = 0.2, 
                          max_attempts = 100, random_state = 2)
          
          # Re-arrange paths
          best_state = re_arrange_path(best_state.tolist())
          # Translate path to store numbers
          best_state_store_nums = []
          for x in best_state:
            store_num = self.all_stores_in_cluster[x]
            best_state_store_nums.append(store_num.store_number)
          print(routes)
          print('The best state found is: ', best_state)
          print(f'Translated store#: {best_state_store_nums}')
          print('The fitness at the best state is: ', best_fitness)
          print(f'Returns for Cluster: {self.cluster_returns} --- Miles per Return: {best_fitness/self.cluster_returns}')
          self.optimal_path['cluster_optimal_route'] = best_state_store_nums
          self.optimal_path['miles_per_retun'] = best_fitness/self.cluster_returns
          self.optimal_path['route_miles'] = best_fitness
          return best_fitness

    def cluster_info(self):
        primary_store_number = self.primary.store_number
        store_nums = [store.store_number for store in self.satelite_stores]
        store_nums.insert(0, primary_store_number)
        stores_in_cluster = [str(store.store_number) for store in self.all_stores_in_cluster]
        export = [self.cluster_id, self.state, round(self.cluster_returns,2), round(self.calc_miles_to_sweep(),2), stores_in_cluster]
        # print(export)
        return export

    def cluster_export(self):
        # Retuns dictionary with the following columns:
        # Primary Store #, Satelite store locations (concat), returns of satelite stores (concat) \
        # primary returns, total cluster return, returns collection path ( concat), route miles, miles per return
        export = {}
        export['cluster_state'] = [self.state]
        export['cluster_total_returns'] = [self.cluster_returns]
        export['primary_store_number'] = [self.primary.store_number]
        export['primary_returns'] = [self.primary.returns]
        export['satellite_store_numbers'] = [str([ x.store_number for x in self.satelite_stores])]
        export['drive_order'] = [str(self.optimal_path['cluster_optimal_route'])]
        export['route_miles'] = [self.optimal_path['route_miles']]
        export['revenue_for_cluster'] = sum([store.store_revenue for store in self.all_stores_in_cluster])
        #print(export)
        return export
