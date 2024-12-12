import pandas as pd
import numpy as np
from datetime import datetime
from collections import Counter 
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

"""
Implementation Reference:
https://medium.com/datafabrica/mastering-e-commerce-product-recommendations-in-python-7c12a4bf0c2c
"""


def generate_recommendations(target_customer: str, cohort, num_recommendations=8):
      """
      returns recommendation for other products to be purchased using rfmTable, based on a cohort of customers with purchase history set as a reference
      Args:
            target_customer : Path to a (.csv) purchase_history file.
            cohort : a pd dataframe with relevant purchase_history in the format provided in the repository
        Returns:
            list: a list of recommended product names in an order.

      """
      user_item_matrix = cohort.groupby('uid')['product_name'].apply(lambda x: ', '.join(x)).reset_index()
      user_item_matrix['product_type'] = cohort.groupby('uid')['product_type'].apply(lambda x: ', '.join(x)).reset_index()['product_type']
      tfidf = TfidfVectorizer()
      tfidf_matrix = tfidf.fit_transform(user_item_matrix['product_type'])
      similarity_matrix = cosine_similarity(tfidf_matrix)
      target_customer_index = user_item_matrix[user_item_matrix['uid'] == target_customer].index[0]
      similar_customers = similarity_matrix[target_customer_index].argsort()[::-1][1:num_recommendations+1]
      target_customer_purchases = set(user_item_matrix[user_item_matrix['uid'] == target_customer]['product_name'].iloc[0].split(', '))
      recommendations = []
      for customer_index in similar_customers:
          customer_purchases = set(user_item_matrix.iloc[customer_index]['product_name'].split(', '))
          new_items = customer_purchases.difference(target_customer_purchases)
          recommendations.extend(new_items)
      return list(set(recommendations))[:num_recommendations]




def recommend(dataset: str, uid: str):
  """
  returns recommended product to be purchased using rfmTable

  Args:
      dataset: Path to a (.csv) purchase_history file.
      uid: user id.

  Returns:
      list: a list of recommended product names in an order.
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

  """
  Recency, Frequency and Monetary Recommendation
  """
  df['purchase_date'] = pd.to_datetime(df['purchase_date'], format='%Y-%m-%d')
  NOW = df['purchase_date'].max()
  rfmTable = df.groupby('uid').agg({'purchase_date': lambda x: (NOW - x.max()).days, 'product_name': lambda x: len(x), 'purchase_price': lambda x: x.sum()})
  rfmTable['purchase_date'] = rfmTable['purchase_date'].astype(int)
  rfmTable.rename(columns={'purchase_date': 'recency', 
                        'product_name': 'frequency',
                        'purchase_price': 'monetary_value'}, inplace=True)
  rfmTable['r_quartile'] = pd.qcut(rfmTable['recency'], q=4, labels=range(1,5), duplicates='raise')
  rfmTable['f_quartile'] = pd.qcut(rfmTable['frequency'], q=4, labels=range(1,5), duplicates='drop')
  rfmTable['m_quartile'] = pd.qcut(rfmTable['monetary_value'], q=4, labels=range(1,5), duplicates='drop')
  rfmTable['r_quartile'] = rfmTable['r_quartile'].astype(str)
  rfmTable['f_quartile'] = rfmTable['f_quartile'].astype(str)
  rfmTable['m_quartile'] = rfmTable['m_quartile'].astype(str)
  rfmTable['RFM_score'] = rfmTable['r_quartile'] + rfmTable['f_quartile'] + rfmTable['m_quartile']

  rfmTable['customer_segment'] = 'Other'

  rfmTable.loc[rfmTable['RFM_score'].isin(['334', '443', '444', '344', '434', '433', '343', '333']), 'customer_segment'] = 'Premium Customer' #nothing <= 2
  rfmTable.loc[rfmTable['RFM_score'].isin(['244', '234', '232', '332', '143', '233', '243']), 'customer_segment'] = 'Repeat Customer' # f >= 3 & r or m >=3
  rfmTable.loc[rfmTable['RFM_score'].isin(['424', '414', '144', '314', '324', '124', '224', '423', '413', '133', '323', '313', '134']), 'customer_segment'] = 'Top Spender' # m >= 3 & f or m >=3
  rfmTable.loc[rfmTable['RFM_score'].isin([ '422', '223', '212', '122', '222', '132', '322', '312', '412', '123', '214']), 'customer_segment'] = 'At Risk Customer' # two or more  <=2
  rfmTable.loc[rfmTable['RFM_score'].isin(['411','111', '113', '114', '112', '211', '311']), 'customer_segment'] = 'Inactive Customer' # two or more  =1

  
  premium = list(set(rfmTable.index))[:len(rfmTable['customer_segment'])]
  df_premium = df[df['uid'].isin(premium)]
  recommendations = generate_recommendations("5qnoytiyjqih5rv99mnwctq6n27t", df_premium, num_recommendations=8)

  return recommendations
  



