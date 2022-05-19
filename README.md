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
- next navigate to the `front/` dir and use python to start up the app.
```bash
cd front/
python3 app.py
```
This startup up will likely throw a couple warnings depending on what your system from tensorflow. Ignore them.
- The server is hosted on "127.0.0.1:5000" so head over there on whatever browser you like and you should be greated by the home screen
- On the home screen to upload an image (png or jpg format) press the browse button, select your image, then press upload. This will take a second or two to process.
![Homepage Screenshot](https://github.com/EnLewis/shopify-image-repo/blob/main/refs/homepage.png)
- Once the upload completes, if successful, it should add it to a table which displays the filename, remote filepath, and the servers best guess of what the photo you just uploaded was.
![Table View](https://github.com/EnLewis/shopify-image-repo/blob/main/refs/table.png)
- You can click `View` to view the image, and see the probabilities of what the server thinks exists in the image.
![Image Prview](https://github.com/EnLewis/shopify-image-repo/blob/main/refs/preview.png)
- You can also remove the image from the database via the delete button.

