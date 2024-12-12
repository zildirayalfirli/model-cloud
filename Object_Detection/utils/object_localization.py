import tensorflow as tf #tensorflow ver 2.18.0
import numpy as np
import cv2 as cv
import pytesseract

from matplotlib import pyplot as plt

def object_localization(img_path, model):
    """
    Localizes the object of interest (receipt) in an image.

    Args:
        img_path (str): Path to the image file.
        model (tf.keras.Model): The object detection model.

    Returns:
        numpy.ndarray: The cropped image containing the localized object.
    """
    
    # MAIN CODE #
    input_size = 244

    # Load the image
    img = cv.imread(img_path)  

    # Convert to RGB if not grayscale
    if len(img.shape) == 3:  # Check if image has 3 channels (color)
        img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)  # Convert to grayscale

    #preprocess the image
    height, width = img.shape
    max_size = max(height, width)
    r = max_size / input_size
    new_width = int(width / r)
    new_height = int(height / r)
    new_size = (new_width, new_height)
    resized = cv.resize(img, new_size, interpolation= cv.INTER_LINEAR)
    new_image = np.zeros((input_size, input_size), dtype=np.uint8)
    new_image[0:new_height, 0:new_width] = resized

    #second preprocessing
    X = [] 
    new_image = new_image.astype(float) / 255.

    X.append(new_image)

    #third preprocessing
    X = np.array(X)
    
    X = np.expand_dims(X, axis=3)

    X = tf.convert_to_tensor(X, dtype=tf.float32)

    result = X
    
    # Object Localization for 
    predictions = model(result) #change

    predicted_box = abs(predictions[1][0] * max_size)
    
    predicted_box = tf.cast(predicted_box, tf.int32)

    predicted_box = abs(predictions[1][0])
    norm_max = max(predicted_box)
    norm_max = norm_max.numpy()

    predicted_box = (predicted_box / norm_max) * max_size
    
    predicted_box = tf.cast(predicted_box, tf.int32)
    predicted_box_value = predicted_box.numpy()
    
    x_min,y_min,x_max,y_max = predicted_box_value
    cropped_struk = img[y_min:y_max, x_min:x_max]
    cropped_struk = np.array(cropped_struk)
    
    return cropped_struk

def ocr_receipt(img_path, model):
    cropped_image = object_localization(img_path, model)
    options = "--psm 6"
    extracted_text = pytesseract.image_to_string(
        cv.cvtColor(cropped_image, cv.COLOR_BGR2RGB), config=options)
    return extracted_text
