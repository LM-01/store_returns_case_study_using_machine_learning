# -*- coding: utf-8 -*-
"""walmart_returns.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1U_17xTVZfBkmUUf6MedXCRZwiHBZuiDx
"""

# -*- coding: utf-8 -*-
"""
Created on Fri Aug 27 11:37:09 2021

@author: lmollinedo
"""

import pandas as pd
import numpy as np
import math
import pickle
from cluster import Cluster
from store import Store
from utils import get_distance, store_sort

"""
Creates clusters of stores based on the distance from the primary stores, and
exports two files. One with the cluster information, and the other containing the list of 
stores in the cluster.
"""

class Solver(Cluster, Store):
    def __init__(self, max_distance, max_returns):
        self.max_distance = max_distance # Max distance from primary store
        self.max_returns = max_returns # Max returns for a cluster
        self.load_data()
        self.clusters = []
        self.cluster_id = 1
        self.networks = []
        self.excluded_states = ['AK','CA','HI']
        self.stores_list = self.create_stores()

    def load_data(self):
        df = pd.read_csv(r'store_returns_analysis.csv')
        df['store_city'] = df['store_city'].str.lower()
        county_data = pd.read_csv(r'cities_data.csv')
        county_data['store_city'] = county_data['city'].str.lower()
        self.states = df.store_state.unique()
        self.merged = df.merge(county_data, left_on=['store_city','store_state'], right_on=['store_city','state_id'], how='left')
                
    def create_stores(self):
        stores_list = []
        for i,row in self.merged.iterrows():
            # print(row['Daily Returns'])
            store = Store(row['Daily Returns'],
                          row['store_city'],
                          row['store_state'],
                          row['store_number'])
            # print(store.state, store.returns)
            store.lat = row['lat']
            store.lng = row['lng']
            stores_list.append(store)
        return stores_list
    
    def find_primary_store_in_state(self, state):
        # Returns an available store with the most returns in a state
        stores_in_state = self.available_stores_in_state(state)
        stores_in_state.sort(reverse=True, key=store_sort)
        if len(stores_in_state) == 0:
            return False
        primary = stores_in_state[0]
        primary.store_type = 'Primary'
        return primary
    
    def cal_distance_to_primary(self, store, primary):
        # Calculates the distance from a store to a primary store
        return round(get_distance(primary.lat, primary.lng, store.lat, store.lng),2)
    
    def available_stores_in_state(self, state):
        return [store for store in self.stores_list if store.state == state 
                and store.paired == False
                and store.store_type != 'Primary'
                and not math.isnan(store.lat)]
    
    def create_cluster(self):
        cluster = Cluster(self.cluster_id)
        self.cluster_id += 1
        return cluster
            
    def run_v2(self):
        # Will clear the clusters and create new routes based on specifications
        self.clusters = []
        for state in self.states:
            if state not in self.excluded_states:
              print(f'Running solver for: {state}')
              loop_run = True
              while loop_run:
                  primary = self.find_primary_store_in_state(state) 
                  if primary != False:
                      # Create a cluster and add a primary
                      cluster = self.create_cluster()
                      cluster.state = state
                      cluster.add_primary(primary)
                      stores_in_state = self.available_stores_in_state(state)
                      # Calculate distance from primary store for every store
                      for store in stores_in_state:
                          store.distance_to_primary = self.cal_distance_to_primary(store, primary)
                      # Calculate ratio                     
                      building_cluster = True
                      while building_cluster:
                        store_to_evaluate = cluster.all_stores_in_cluster[-1]
                        print(f'Evaluating store {store_to_evaluate.store_number}')
                        # if store_to_evaluate.store_number == 1436:
                        #     print('Wait')
                        next_stores = self.calculate_ratio(state, store_to_evaluate)
                        ### CALCULATE OPTIMAL PATH HERE ###
                        
                        ###################################
                        if len(next_stores) <= 2:
                          # Close the cluster if there are not enough stores 
                            print(f'Length is {len(next_stores)}')
                            loop_run = False
                            building_cluster = False
                        else:
                            cluster.add_store(next_stores[0][0])
                            path_miles = cluster.get_optimial_path()
                            # Limits cluster to max 50 miles for the optimal path
                            if path_miles > 50:
                              cluster.remove_last_store_added()
                              path_miles = cluster.get_optimial_path()
                              building_cluster = False
                        if path_miles == None or path_miles >= 50:
                            building_cluster = False

                      self.clusters.append(cluster)
                  else:
                      loop_run = False
              else:
                pass
            
    def calculate_ratio(self,state, source_store):
        # Calculates the ratio from a "source_store" to all available stores and returns the top one
        available_stores = self.available_stores_in_state(state)
        ratios = []
        for i, dest_store in enumerate(available_stores):
            #print(i)
            ratio = round(dest_store.returns / (source_store.calc_distance_to_other_store(dest_store) + dest_store.distance_to_primary),5)
            ratios.append([dest_store, ratio])
        ratios = [x for x in ratios if not math.isnan(x[1])]
        ratios.sort(reverse = True, key=lambda x: x[1])
        stores = [pair for pair in ratios if not math.isnan(pair[0].lat)]
        print(source_store.store_number , len(ratios))
        return stores

    def export(self):
        print('Printing Export')
        # Exports cluster information
        e_columns =['cluster_id','state','cluster_returns','miles_to_sweep','stores_in_cluster']
        cluster_data = []
        store_data = []
        for cluster in self.clusters:
            cluster_data.append(cluster.cluster_info())
        df1 = pd.DataFrame(data=cluster_data, columns=e_columns)
        #print(df1.tail(50))
        df1.to_csv('exports/cluster_list.csv',index=False)
        
        # Cluster ID , Store
        # Exports stores list for each cluster
        clusterinfo = []
        cluster_columns = ['cluster_id','store_number','store_returns']
        for cluster in self.clusters:
            data = [cluster.cluster_id, cluster.primary.store_number, cluster.primary.returns]
            clusterinfo.append(data)
            for store in cluster.satelite_stores:
                data = [cluster.cluster_id, store.store_number, store.returns]
                clusterinfo.append(data)
        df2 = pd.DataFrame(data=clusterinfo, columns=cluster_columns)
        #print(df2.tail(50))
        df2.to_csv(r'exports/cluster_store_list.csv',index=False)

# Calculate the optimal path
def calculate_optimal_paths(solver):
  routes = []
  cluster_exports = []
  for i,cluster in enumerate(solver.clusters):
    if i != None:
      #print(i)
      best_route = []
      connections = cluster.get_optimial_path()
      if len(cluster.all_stores_in_cluster) > 1:
        exports = cluster.cluster_export()
        cluster_exports.append(exports)
  return cluster_exports

#with open('/content/solver-saved', 'rb') as file:
#  solver = pickle.load(file)

def save_model(solver):
  filename = 'solver-saved-v2'
  outfile = open(filename, 'wb')
  pickle.dump(solver,outfile)
  outfile.close()
  print('Model Saved!')

def update_store_data(solver):
  new_store_data = pd.read_csv(r'wm_stores_v2.csv')
  new_store_data.dropna(inplace=True)
  new_store_data['Zip Code'] = new_store_data['Zip Code'].astype(int)
  new_store_data.info()
  # Adds in the new values to the existing model
  for i,cluster in enumerate(solver.clusters):
    for j,store in enumerate(cluster.all_stores_in_cluster):
      #if i == 0 and j == 0:
      row = new_store_data.loc[new_store_data['store_number'] == store.store_number]
      if not row.empty and row['LAT'].values[0] != 0:
        zip = row['Zip Code'].values[0]
        returns = row['Daily Returns'].values[0]
        lat = row['LAT'].values[0]
        lng = row['LNG'].values[0]
        store.returns = returns
        store.zip_code = zip
        store.lat = lat
        store.lng = lng

def test_new_import(solver):
  test_store = solver.clusters[0].all_stores_in_cluster[2]

def full_store_list(solver):
  #Returns an array with all the stores available in solver and clusters
  stores = []
  for i,cluster in enumerate(solver.clusters):
    for j,store in enumerate(cluster.all_stores_in_cluster):
      stores.append(store)
  return stores

