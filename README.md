# Shopify Data Engineer Challenge
Here in lies a simple image webserver built using Flask for front/back end, tensorflow for some simple image classification, and sqlite as a database.

### QuickStart
- Make sure you have a valid install of python. For best results use a Ubuntu 20.04 systems since that is what this was developed and tested for
- Clone this repo to your machine and ideally start up a python virtual env for easier package management.
- Install the projects requirements by running<br>
```bash
pip install -r requirements.txt
```
This will probably take some time since it needs to get the pre-build tensorflow models we use in this project
- Next navigate to the `front/` dir.
```bash
cd front/
```
- Now we have to load up our tile database for the image mosaic feature. For the quickstart guide we are going to use the [CIFAR-10](https://www.cs.toronto.edu/~kriz/cifar.html) tiny image dataset.
- Download the image dataset from [this link](https://www.cs.toronto.edu/~kriz/cifar-10-python.tar.gz) and untar it to the `front/` directory. We should have a `front/cifar-10-batches-py` directory now.
```bash
# We use wget here, you can download it however you like
wget https://www.cs.toronto.edu/~kriz/cifar-10-python.tar.gz
tar -xf cifar-10-python.tar.gz
```
- Now we can start out app with python.
```bash
python3 app.py
```
This startup up will likely throw a couple warnings from tensorflow depending on your system. Ignore them.
- The server is hosted on "127.0.0.1:5000" so open up whatever browser you like and paste that address into the address bar, hit enter, and you should be greeted by the home screen.
- On the home screen to upload an image (png or jpg format) press the browse button, select your image, then press upload. This will take a second or two to process.
![Homepage Screenshot](https://github.com/EnLewis/shopify-image-repo/blob/main/refs/homepage.png)
- Once the upload completes, if successful, it should add it to a table which displays the filename, remote filepath, and the servers best guess of what the photo you just uploaded was.
![Table View](https://github.com/EnLewis/shopify-image-repo/blob/main/refs/table.png)
- You can click `View` to view the image, and see the probabilities of what the server thinks exists in the image. You can also remove the image from the database via the delete button. This will remove the image from the remote database completely.
![Image Preview](https://github.com/EnLewis/shopify-image-repo/blob/main/refs/preview.png)
- From this page if you click the "View Image as Mosaic" button you will be brought to a page displaying the original image and an image mosaic constructed from the pixel values of the original image and the mean RGB values of images from a pre-loaded image tile database.
![Mosaic View](https://github.com/EnLewis/shopify-image-repo/blob/main/refs/mosaic.png)

### Features
#### Upload
The upload feature takes in an image from the user and does some operations on it...
1. The image is saved to disk first
2. Then we use a pre-loaded image-classification net to try and classify the contents of the users image.
```python
# Load the pre-built Keras EfficientNet model
# One could extend this to use models trained by hand or other models using different training sets
model = EfficientNetB0(weights='imagenet')
```
3. A smaller thumbnail of the image is saved to disk as well.
4. After classification, the meta_data of the image is saved to an SQL database.
```python
# Save thumbnail to disk and attempt to classify
best_guesses = save_thumbnaill_and_classify(app.config['UPLOAD_FOLDER'], filename)
# Set your threshold for the worst match you will tolerate for considering a tag to be valid
threshold = 0
best_guess = best_guesses[0][1]
tags = [ Tag(tag_name=guess[1], tag_prob=guess[2]) for guess in best_guesses if guess[-1] > threshold]
...
 # Add to database
new_entry = DBImg(best_tag=best_guess, filename=filename, filepath=filepath)
new_entry.tags.extend(tags)
try:
    db.session.add(new_entry)
    db.session.add_all(tags)
    db.session.commit()
except Exception as e:
    print(e)
    return "ERROR WITH DB FUNCS"
```
The goal of this feature was to show a simple way of taking in an image and processing it so that it could be searched or referenced later based on its contents (tags) without having to reporocess it.
#### Mosaic
The mosaic features uses small images (32,32) as tiles to recreate a source image according the proximity of the tiles and the source image mean RGB values. The tile images are stored into an hdf5 file along with their meta data and RGB mean values as numpy arrays. The goal of this feature was to showcase a more efficient way of saving and retrieving very large numbers of image files in a data format that is very friendly to image processing and machine learning libraries like `keras`.
#### Future Extensions
##### Searchability
The tags in the image SQL database provide a way to search for the content of images without having to reprocess the images themselves. The hdf5 format is also friendly to this sort of grouping and tagging. So if the application was expanded to want to search the tile databse as well it could be easily one by simply inserting images on paths based on their tags. `i.e: /animal/fourlegs/koala`.
##### Custom models
Different machine learning models could be trained and plugged in depending on the users needs. This would simply require replacing the `model` global seen earlier.
##### Adding data to the model
The images that are uploaded are processed into thumbnails these thumbnails could be used to improve the model for classification.
##### Adding to the mosaic
The thumbnails, or the images themselved could be resized and added to the tiles database to grow it overtime as the database grows.
##### More image processing
Since the data inside the tile database is stored as numpy arrays, it is very friendly to any kind of image processing one desires. If the image database images where added to the hdf5 formatted file, those images could be very easily processed as well.