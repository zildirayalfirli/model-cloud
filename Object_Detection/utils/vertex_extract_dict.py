import vertexai
from vertexai.preview.generative_models import GenerativeModel

from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials

import requests
import json
import re
import os

def geocode_address(address, credentials):
    """
    Geocodes a given address using the Google Maps Geocoding API and service account credentials.

    Args:
        address (str): The address to be geocoded.
        credentials (google.oauth2.credentials.Credentials): An instance of Google service account credentials containing a valid token.

    Returns:
        tuple(float, float) or None, None: 
            - A tuple containing the latitude and longitude if successful,
            - None, None if geocoding fails or the request fails.
    """

    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
      "address": address,
      "key": credentials.token
    }

    headers = {
      "Authorization": f"Bearer {credentials.token}"
    }
    
    response = requests.get(url, params=params, headers=headers)

    if response.status_code == 200:
      response_json = response.json()
      if response_json['status'] == 'OK':
        # Process the geocoding results
        for result in response_json['results']:
          location = result['geometry']['location']
          return location['lat'], location['lng']
      else:
        print("Geocoding failed:", response_json['status'])
        return None, None
    else:
      print("Request failed with status code:", response.status_code)
      return None, None

def extract_dict(receipt_ocr: str, key_path: str, uid: str, email: str):
    """
        Extract relevant informations parsed from an ocr of a receipt into a structured dictionary

    Args:
        receipt_ocr (string): a string from applying OCR to a shopping receipt.
        key_path  : a string to a path containing the json key for google vertex ai.
        uid       : user id.
        email     : user email.
    
    Returns:
        data: a dictionary of relevant informations, the contain is provided below in the prompt:
    """
    if len(uid) != 20:
      raise ValueError('UID is not 20 characters long')
    if re.fullmatch(r"^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$", email) is None:
      raise ValueError('Email is not valid')

    prompt = '''Provided below is an OCR of Indonesian shopping receipt. You will extract the relevant informations from the OCR text.

    Please return a string that needs to follow the format below (only return the dictionary string and nothing else).
    The returned string should be in the format of how one would define python dictionaries. Also perform typo correction on the OCR text
    before parsing it.

    Do not include escape characters in the values inside the dictionary. If any part in the OCR text contain single or double quotation, drop them.


    Dictionary format:
    extracted_information = {

    "purchase_date" : [], #(String) In ISO 8601 format, just one value in this key. If none, return todays date.

    "purchase_address" : [], #(String) from Indonesian address format, return both the vendor name and its address in one string, just one value in this key. Do not use escape characters.

    "product_name" : [], #(String) directly from the receipt, you need to pass all the products listed in the receipt here, more than one value

    "purchase_price" : [] #(Float) directly from the receipt, same length as the product_name key

    "product_type" : [] #(String) product type of the product, refer to the product type list below, and predict only using the categories provided

    }



    product_type_reference = ["minuman manis", "minuman sehat", "personal hygiene", "makanan manis", "makanan gurih",

    "unknown", "makanan pokok", "produk dewasa"

    ]



    OCR text:

    '''
    '''
    Initializing Google Vertex AI
    '''
    credentials = Credentials.from_service_account_file(
        key_path,
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )

    if credentials.expired:
      credentials.refresh(Request())

    PROJECT_ID = "capstone-bangkit-d0ca4"
    REGION = "us-central1"
    vertexai.init(project=PROJECT_ID, location=REGION, credentials = credentials)

    '''
    Configuring the prompt
    '''
    prompt = prompt + receipt_ocr

    prompt = prompt.replace("\'", '')

    generative_multimodal_model = GenerativeModel("gemini-1.5-pro-002")
    response = generative_multimodal_model.generate_content([prompt])

    text = response.candidates[0].content.parts
    text = text[0].text

    json_string = re.search(r'\{.*\}', text, re.DOTALL).group(0)
    json_string = json_string.replace("'", '"')

    with open('llm_output.json', 'w') as file: #need this to capture output, do not remove
        file.write(json_string)

    with open('llm_output.json', 'r') as file:
        data = json.load(file)

    os.remove('llm_output.json')

    
    data['uid'] = [uid]
    data['email'] = [email]
    data['quantity'] = [1]

    #get long lat
    lat, long = geocode_address(data['purchase_address'][0], credentials)
    data['long'] = [long]
    data['lat'] = [lat]

    #duplicate dict keys with only single value to match the length of other keys
    max_len = max(len(v) for v in data.values())

    # Duplicate single-value keys to match the maximum length
    for key, value in data.items():
        if len(value) == 1:
            data[key] = value * max_len

    return data
