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
- The server is hosted on "127.0.0.1:5000" so open up whatever browser you like and pasted that address into the url bar, hit enter, and you should be greated by the home screen.
- On the home screen to upload an image (png or jpg format) press the browse button, select your image, then press upload. This will take a second or two to process.
![Homepage Screenshot](https://github.com/EnLewis/shopify-image-repo/blob/main/refs/homepage.png)
- Once the upload completes, if successful, it should add it to a table which displays the filename, remote filepath, and the servers best guess of what the photo you just uploaded was.
![Table View](https://github.com/EnLewis/shopify-image-repo/blob/main/refs/table.png)
- You can click `View` to view the image, and see the probabilities of what the server thinks exists in the image. You can also remove the image from the database via the delete button. This will remove the image from the remote database completely.
![Image Preview](https://github.com/EnLewis/shopify-image-repo/blob/main/refs/preview2.png)
- From this page if you click the "View Image as Mosaic" button you will be brought to a page displaying the original image and an image mosaic constructed from the pixel values of the original image and the mean RGB values of images from a pre-loaded image tile database.
![Mosaic View](https://github.com/EnLewis/shopify-image-repo/blob/main/refs/mosaic.png)

### Features
#### Upload
#### Mosaic
#### Future Extensions
