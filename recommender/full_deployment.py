import warnings
import pandas as pd
import re
import json
from Object_Detection.utils.object_localization import ocr_receipt  # Fixed import
from Object_Detection.utils.vertex_extract_dict import extract_dict as ved
from recommender.utils.product_recommender import recommend as pr
from recommender.utils.cheap_close import cheap_proximity_rec as cc


def full_deployment(key_path: str, test_path: str, dataset_path: str, uid: str, email: str, model, lon: float, lat: float):
    """
    Takes a picture of a receipt, performs object localization for the receipt, uses OCR on cropped localized image,
    then generates recommended places to get similar items for cheaper and closer.

    Args:
      key_path (str): Path to the Google Cloud service account JSON key file.
      test_path (str): Path to the image file of the receipt.
      dataset_path (str): Path to the purchase history dataset.
      uid (str): User ID.
      email (str): User email address.
      model (Any): The object detection model to be used for receipt localization.
      lon (float): User's longitude coordinate.
      lat (float): User's latitude coordinate.

    Returns:
      pd.DataFrame: A dataframe sorted by distance from user's location, offering the cheapest price, 
                    at the most up-to-date of user's previously purchased items and recommended items based on RFM analysis.
    """
    df = pd.read_csv(dataset_path)
    
    if df.empty:
        raise ValueError("DataFrame is empty. Please check the dataset file in the provided path.")
    if 'uid' not in df.columns:
        raise ValueError("uid column is missing from the dataset")
    if re.fullmatch(r"^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$", email) is None:
        raise ValueError('Email is not valid')
    if 'long' not in df.columns:
        raise ValueError("long column is missing from the dataset")
    if 'lat' not in df.columns:
        raise ValueError("lat column is missing from the dataset")
    
    warnings.simplefilter(action='ignore', category=FutureWarning)
    max_retries = 3  
    for attempt in range(max_retries + 1):
        try:
            struk = ocr_receipt(test_path, model)  # Properly calls the imported function
            data = ved(struk, key_path, uid, email)
            data = pd.DataFrame(data)
            break
        except json.JSONDecodeError as e:
            if attempt == max_retries:
                raise
            else:
                print(f"JSONDecodeError encountered on attempt {attempt+1}. Retrying...")

    df = pd.concat([df, data], ignore_index=True)
    df.to_csv(dataset_path, index=False)
    test_rec = pr(dataset_path, uid)
    end_rec = cc(
        dataset=dataset_path,
        uid=uid,
        product_list=test_rec,
        lon=lon,
        lat=lat
    )
    return end_rec
