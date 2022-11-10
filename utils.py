from math import radians, cos, sin, asin, sqrt

def get_distance(lat1, lon1, lat2, lon2):
    # Returns distance between two lat/lon points in KM
    # The math module contains a function named radians which converts from degrees to radians.
    lon1 = radians(lon1)
    lon2 = radians(lon2)
    lat1 = radians(lat1)
    lat2 = radians(lat2)
 
    # Haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371 # Radius of earth in kilometers. Use 3956 for miles
    
    #Display the result
    # print("Distance is: ",c*r,"Kilometers")
    return c*r

def store_sort(x):
    return x.returns

def re_arrange_path(x):
  # Finds the primary store (0), and rearranges the path \
  # so that it starts at the primary store
  zero = x.index(0)
  to_move = x[:zero]
  start = x[zero:]
  new_list = start + to_move
  return new_list

def sort_sublist(values, e_index, reverse = False):
    return values.sort(key= lambda x: x[1], reversed = reverse)
