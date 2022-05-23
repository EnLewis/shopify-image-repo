# Image classifications imports
import tensorflow as tf
from tensorflow.keras.applications.efficientnet import EfficientNetB0
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.efficientnet import preprocess_input, decode_predictions
import numpy as np

# Mosaic and hdf5 imports
from scipy import spatial
from pathlib import Path
from PIL import Image
import pickle
import h5py
import os

HDF5_DIR = Path("static/server_db/sources")

# Load the pre-built Keras EfficientNet model
# One could extend this to use models trained by hand or other models using different training sets
model = EfficientNetB0(weights='imagenet')

# Set batch size for training and validation
batch_size = 32

THMBN_HEIGHT = 224
THMBN_WIDTH = 224


def save_thumbnaill_and_classify(db_dir, img_name):
    """Save thumbnail to disk and attempt image classification
    
    Returns: 
        list of tuples (class, description, probability) 
        corresponding to image classification.
    """

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
    """Attempt image classification
    
    Returns: 
        list of tuples (class, description, probability) 
        corresponding to image classification.
    """

    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x)
    preds = model.predict(x)
    # decode the results into a list of tuples (class, description, probability)
    # (one such list for each sample in the batch)
    return decode_predictions(preds, top=10)[0]


def pickle_to_hdf5(data_dir):
    """From a pickled image dataset, save the images to an hdf5 file"""

    # Unpickle function provided by the CIFAR hosts
    def unpickle(file):
        with open(file, "rb") as fo:
            dict = pickle.load(fo, encoding="bytes")
        return dict
    images, labels = [], []
    for batch in data_dir.glob("data_batch_*"):
        batch_data = unpickle(batch)
        for i, flat_im in enumerate(batch_data[b"data"]):
            im_channels = []
            # Each image is flattened, with channels in order of R, G, B
            for j in range(3):
                im_channels.append(
                    flat_im[j * 1024 : (j + 1) * 1024].reshape((32, 32))
                )
            # Reconstruct the original image
            images.append(np.dstack((im_channels)))
            # Save the label
            labels.append(batch_data[b"labels"][i]) 
    store_to_mosaic_hdf5(images,labels)
    return True

def store_to_mosaic_hdf5(images, labels):
    """ Stores an array of images to HDF5.

    Args:
        images: images array, (N, 32, 32, 3) to be stored
        labels: labels array, (N, 1) to be stored
    """

    # TODO: crop images to 32,32
    num_images = len(images)
    means = []
    for image in images:
        means.append(np.array(image).mean(axis=0).mean(axis=0))
    with h5py.File(HDF5_DIR / f"mosaic_tiles.h5", "w") as file:
        dataset = file.create_dataset("images", np.shape(images), h5py.h5t.STD_U8BE, data=images)
        meta_set = file.create_dataset("meta", np.shape(labels), h5py.h5t.STD_U8BE, data=labels)
        means = file.create_dataset("means", np.shape(means),  h5py.h5t.STD_U8BE, data=means)

def read_images_from_hdf5(path_to_tiles_db="mosaic_tiles.h5"):
    """ Reads image from HDF5.
    Args:
        path_to_tiles_db: path to the hdf5 that has our tiles data in it.

    Returns:
        images: images array, (N, 32, 32, 3) to be used.
        labels: associated meta data, int label (N, 1).
        means: mean array (N, 3) of the RGB means of each tile.
    """

    images, labels = [], []
    # Open the HDF5 file
    with h5py.File(HDF5_DIR / path_to_tiles_db, "r+") as file:
        images = np.array(file["/images"]).astype("uint8")
        labels = np.array(file["/meta"]).astype("uint8")
        means = np.array(file["/means"]).astype("uint8")
    return images, labels, means

def img_to_mosaic(img_path):
    """Convert an image to a mosaic of images from our mosaic tile database"""

    tiles, _, colors = read_images_from_hdf5()

    tile_size = tiles.shape[1:3]

    # Resize the source photo for ease of processing
    prime_photo = Image.open(img_path)
    width = int(np.round(prime_photo.size[0] / tile_size[0]))
    height = int(np.round(prime_photo.size[1] / tile_size[1]))
    resized_photo = prime_photo.resize((width, height))
    
    # Setup tree structure for tiles to get euclidean distance
    # between RGB values of the source image and the tiles
    tree = spatial.KDTree(colors)
    closest_tiles = np.zeros((width, height), dtype=np.uint32)

    # Determine best tiles to use
    for i in range(width):
        for j in range(height):
            closest = tree.query(resized_photo.getpixel((i, j)))
            closest_tiles[i, j] = closest[1]
    output = Image.new('RGB', prime_photo.size)
    
    # Draw tiles to a final image
    for i in range(width):
        for j in range(height):
            # Offset of tile
            x, y = i*tile_size[0], j*tile_size[1]
            # Index of tile
            index = closest_tiles[i, j]
            # Draw tile
            tile_image = Image.fromarray(tiles[index].astype('uint8'), 'RGB')
            output.paste(tile_image, (x, y))

    return output