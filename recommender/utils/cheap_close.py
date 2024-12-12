import pandas as pd
import numpy as np
from math import radians, sin, cos, acos
from geopy.distance import great_circle

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float):
    """
    Calculates the Haversine distance between two points on a sphere.

    Args:
        lat1 (float): Latitude of the first point in degrees.
        lon1 (float): Longitude of the first point in degrees.
        lat2 (float): Latitude of the second point in degrees.
        lon2 (float): Longitude of the second point in degrees.

    Returns:
        float: Distance in kilometers.
    """

    """
    Initialization check
    """
    if lon1<-180 or lon1>180:
      raise ValueError("Longitude must be between -180 and 180")
    if lat1<-90 or lat1>90:
      raise ValueError("Latitude must be between -90 and 90")
    if lon2<-180 or lon2>180:
      raise ValueError("Longitude must be between -180 and 180")
    if lat2<-90 or lat2>90:
      raise ValueError("Latitude must be between -90 and 90")

    """
    Calculate Haversine Distance
    """
    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)

    distance = 6371.0 * acos(sin(lat1)*sin(lat2)+cos(lat1)*cos(lat2)*cos(lon2-lon1))
    
    return distance

def cheap_proximity_rec(dataset: str, uid: str, product_list: list[str], lon: float, lat: float):
  """
  returns past purchased products and recommended products with cheaper price and in closer proximity to user

  Args:
      dataset: Path to a (.csv) purchase_history file.
      uid: user id.
      product_list: a list of recommended product (parsed from other util function that recommends product to user based on purchase history similarity).
      lon : longitude of user.
      lat : latitude of user.

  Returns:
      temp_df: a data frame of lately purchased product by user, and recommended based on similarity to user, sorted by the shortest distance (in kilometers), 
      latest date (up-to-date price), at the cheapest price.
  """

  df = pd.read_csv(dataset)

  """
  Initialization check
  """
  if df.empty:
    raise ValueError("DataFrame is empty. Please check the dataset file.")
  if 'uid' not in df.columns:
    raise ValueError("uid column is missing from the dataset")
  if 'product_name' not in df.columns:
    raise ValueError("product_name column is missing from the dataset")
  if 'product_type' not in df.columns:
    raise ValueError("product_type column is missing from the dataset")
  if 'purchase_date' not in df.columns:
    raise ValueError("purchase_date column is missing from the dataset")
  if 'purchase_price' not in df.columns:
    raise ValueError("purchase_price column is missing from the dataset")
  if 'long' not in df.columns:
    raise ValueError("long column is missing from the dataset")
  if 'lat' not in df.columns:
    raise ValueError("lat column is missing from the dataset")
  if df[df['uid'] == uid].empty:
    raise ValueError("uid not found, please input the user's uid to the purchase history dataset first")
  if len(product_list) != 8:
    raise ValueError("Product list must have exactly 8 items")
  if lon<-180 or lon>180:
    raise ValueError("Longitude must be between -180 and 180")
  if lat<-90 or lat>90:
    raise ValueError("Latitude must be between -90 and 90")

  df = pd.read_csv(dataset)

  """
  Recommend cheaper products at close proximity to user
  """
  df = df[df['product_name'].isin(product_list)]

  #calculate km distance to users
  slong = radians(float(lon))
  slat = radians(float(lat))
  
  #df['distance'] = df.apply(lambda row: haversine_distance(row['lat'], row['long'], slat, slong), axis=1)
  df['distance'] = df.apply(lambda row: great_circle((row['lat'], row['long']), (lat, lon)).kilometers, axis=1)

  count_trans = df[df['uid'] == uid].shape[0]
  if count_trans <= 5 and count_trans >= 1:
    temp_df = df[df['uid']==uid]
    temp_df = temp_df.sort_values(by='purchase_date', ascending=False)

    recent_prod = df['product_name'][:count_trans].tolist()

  else:
    temp_df = df[df['uid']==uid]
    temp_df = temp_df.sort_values(by='purchase_date', ascending=False)

    recent_prod = df['product_name'][:5].tolist()

  temp_df = df[df['product_name'].isin(recent_prod) | df['product_name'].isin(product_list)]
  temp_df = temp_df.sort_values(by=['distance', 'purchase_date', 'purchase_price',], ascending=[True,False,True])
  temp_df = temp_df.drop(['uid', 'email', 'age', 'quantity'], axis=1)

  return temp_df
