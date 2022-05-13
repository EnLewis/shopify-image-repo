from pathlib import Path

disk_dir = Path("data/disk/")
lmdb_dir = Path("data/lmdb/")
hdf5_dir = Path("data/hdf5/")

disk_dir.mkdir(parents=True, exist_ok=True)
lmdb_dir.mkdir(parents=True, exist_ok=True)
hdf5_dir.mkdir(parents=True, exist_ok=True)

from PIL import Image
import csv
import numpy as np

import lmdb
import pickle

import h5py

class CIFAR_Image:
    def __init__(self, image, label) -> None:
        self.channels = image.shape[2]
        self.size = image.shape[:2]

        self.image = image.tobytes()
        self.label = label

    def get_image(self):
        image = np.frombuffer(self.image, dtype=np.uint8)
        return image.reshape(*self.size, self.channels)

def store_images_disk(images, labels):
    num_images = len(images)

    for i, image in enumerate(images):
        Image.fromarray(image).save(disk_dir / f"{i}.png")

    with open(disk_dir / f"{num_images}.csv", "w") as csvfile:
        writer = csv.writer(csvfile, delimiter=" ", quotechar="|", quoting=csv.QUOTE_MINIMAL)
        for label in labels:
            writer.writerow([label])

def store_images_lmdb(images, labels):
    num_images = len(images)

    map_size = num_images * images[0].nbytes * 10

    env = lmdb.open(str(lmdb_dir / f"{num_images}_lmdb"), map_size=map_size)

    with env.begin(write=True) as txn:
        for i in range(num_images):
            value = CIFAR_Image(images[i], labels[i])
            key = f"{i:08}"
            txn.put(key.encode("ascii"), pickle.dumps(value))
    env.close()

def store_images_hdf5(images, labels):
    num_images = len(images)

    file = h5py.File(hdf5_dir / f"{num_images}_many.h5", "w")

    dataset = file.create_dataset("images", np.shape(images), h5py.h5t.STD_U8BE, data=images)
    metaset = file.create_dataset("meta", np.shape(labels), h5py.h5t.STD_U8BE, data=labels)

    file.close()

def store_single_disk(image, image_id, label):
    Image.fromarray(image).save(disk_dir / f"{image_id}.png")

    with open(disk_dir / f"{image_id}.csv", "wt") as csvfile:
        writer = csv.writer(csvfile, delimiter=" ", quotechar="|", quoting=csv.QUOTE_MINIMAL)

        writer.writerow([label])

def store_single_lmdb(image, image_id, label):
    map_size = image.nbytes * 10

    env = lmdb.open(str(lmdb_dir / f"single_lmdb"), map_size=map_size)

    with env.begin(write=True) as txn:
        value = CIFAR_Image(image, label)
        key = f"{image_id:08}"
        txn.put(key.encode("ascii"), pickle.dumps(value))
    
    env.close()

def store_single_hdf5(image, image_id, label):

    file = h5py.File(hdf5_dir / f"{image_id}.h5", "w")

    dataset = file.create_dataset("image", np.shape(image), h5py.h5t.STD_U8BE, data=image)
    meta_set = file.create_dataset("meta", np.shape(label), h5py.h5t.STD_U8BE, data=label)

    file.close()

_store_single_funcs = dict(
    disk=store_single_disk, lmdb=store_single_lmdb, hdf5=store_single_hdf5
)