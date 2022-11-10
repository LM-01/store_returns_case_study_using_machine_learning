from utils import get_distance

class Store:
    def __init__(self, returns, city, state, store_num):
        self.rev_per_unit = 6.51
        self.returns = returns 
        self.city = city
        self.state = state
        self.store_number = store_num
        self.paired = False
        self.lat = 0
        self.lng = 0
        self.distance_to_primary = None
        self.store_type = None
        self.neighbor_stores = [] #sublist of [store_number, distance_to_neighbor, returns]
        self.neighbor_capacity = None
        self.store_revenue = self.returns * self.rev_per_unit
        self.rejected = False
      
    def reset_store(self):
      self.paired = False
      self.distance_to_primary = None
      self.store_type = None
    
    def calc_distance_to_other_store(self, other_store):
        distance = get_distance(other_store.lat, other_store.lng, self.lat, self.lng)
        if distance == 0:
          distance = 3 # Minimum store distance
        return round(distance,2)
    
    def calc_neighbor_capacity(self):
        cap = 0
        for neighbor in self.neighbor_stores:
            cap += neighbor[2]
        self.neighbor_capacity = cap
        return cap