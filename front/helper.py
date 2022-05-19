import tensorflow as tf
from tensorflow.keras.applications.efficientnet import EfficientNetB0
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.efficientnet import preprocess_input, decode_predictions
import numpy as np
import os

model = EfficientNetB0(weights='imagenet')

# Set batch size for training and validation
batch_size = 32

THMBN_HEIGHT = 32
THMBN_WIDTH = 32


def save_to_disk(db_dir, img_name):
    img = image.load_img(f"{db_dir}/{img_name}", target_size=(224, 224))
    thumbnail = tf.image.resize(img, (THMBN_HEIGHT, THMBN_WIDTH))
    image.save_img(f"{db_dir}/.thumbnails/thb_{img_name}", thumbnail)
    
    return classify_image(img)

def delete_from_disk(filepath, filename):
    try:
        os.remove(filepath)
        thumbnail_path = '/'.join(filepath.split("/")[0:-1]) + "/.thumbnails/thb_" + filename
        os.remove(thumbnail_path)
    except FileNotFoundError as e:
        return f"ERROR {filename} or thb_{filename} not found!"


def classify_image(img):
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x)
    preds = model.predict(x)
    # decode the results into a list of tuples (class, description, probability)
    # (one such list for each sample in the batch)
    return decode_predictions(preds, top=10)[0]
