# Import functions from helper file
from helper import img_to_mosaic, pickle_to_hdf5, save_thumbnaill_and_classify, delete_from_disk

# UI imports
from flask import Flask, render_template, url_for, flash, request, redirect, send_from_directory
from werkzeug.utils import secure_filename
from base64 import b64encode
from io import BytesIO

# Database imports
from flask_sqlalchemy import SQLAlchemy
from pathlib import Path
from datetime import datetime
import os

UPLOAD_FOLDER = 'static/server_db/sources'
ALLOWED_EXTENSIONS = set(['png', 'jpeg', 'jpg'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///image_database.db'

db = SQLAlchemy(app)

# Table for storing the images metadata
class DBImg(db.Model):
    __tablename__ = "dbimgs"
    id = db.Column(db.Integer, primary_key=True)
    tags = db.relationship("Tag", backref="dbimg", lazy="dynamic", cascade="all, delete")
    
    best_tag = db.Column(db.String(200), nullable=True)
    filename = db.Column(db.String(200), nullable=False)
    filepath = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<DBImg {self.id}>'

# Table for storing the tags determined by image classification for an image
class Tag(db.Model):
    __tablename__ = "tags"
    id = db.Column(db.Integer, primary_key=True)
    img_id = db.Column(db.Integer, db.ForeignKey('dbimgs.id'))
    
    tag_name = db.Column(db.String(100), nullable=True)
    tag_prob = db.Column(db.Numeric(precision=5, asdecimal=True, decimal_return_scale=None))
    
    def __repr__(self):
        return f'<Tag {self.id}>'    

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    entries = DBImg.query.order_by(DBImg.date_created).all()
    return render_template('index.html', entries=entries)

@app.route('/upload', methods=['GET', 'POST'])
def upload_img():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'img' not in request.files:
            flash('No file part')
            return redirect(request.url)
        img = request.files['img']
        # if user does not select file, browser also
        # submit an empty part without filename
        if img.filename == '':
            flash('No selected file')
            return redirect(request.url)
        # Valid image received, MOST OF IMPORTANT CODE HERE
        if img and allowed_file(img.filename):
            # Save file
            filename = secure_filename(img.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            img.save(filepath)
            
            # Save thumbnail to disk and attempt to classify
            best_guesses = save_thumbnaill_and_classify(app.config['UPLOAD_FOLDER'], filename)
            # Set your threshold for the worst match you will tolerate for considering a tag to be valid
            threshold = 0
            best_guess = best_guesses[0][1]
            tags = [ Tag(tag_name=guess[1], tag_prob=guess[2]) for guess in best_guesses if guess[-1] > threshold]
            
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
            return redirect('/')
        else:
            flash('File must be a png or jpg format.')
            return redirect(request.url)
    else:  
        return redirect('/')

    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''

@app.route('/delete/<int:id>')
def delete(id):
    entry_to_delete = DBImg.query.get_or_404(id)

    delete_from_disk(entry_to_delete.filepath, entry_to_delete.filename)
    try:
        db.session.delete(entry_to_delete)
        db.session.commit()
        return redirect('/')
    except Exception as e:
        print(e)
        return 'ERROR ON DELETE'

@app.route('/view/<int:id>')
def view(id):
    entry_to_view = DBImg.query.get_or_404(id)

    return render_template("view.html", entry = entry_to_view, tags=entry_to_view.tags)

@app.route('/view/<int:id>/mosaic')
def view_mosaic(id):
    entry_to_view = DBImg.query.get_or_404(id)
    
    # Convert the image to a mosaic of images from out tile dataset
    mosaic = img_to_mosaic(entry_to_view.filepath)

    # Convert the image to uri so that we can display it without storing to disk
    img_io = BytesIO()
    mosaic.save(img_io, "JPEG", quality=70)
    img_io.seek(0)
    encoded = b64encode(img_io.read())
    encoded = encoded.decode('ascii')
    mime = "image/jpeg"
    uri = f"data:{mime};base64,{encoded}"
    return render_template("mosaic_view.html", entry = entry_to_view, uri=uri)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

if __name__ == "__main__":
    app.secret_key = "super secret key"
    
    # Setup directories for the database
    db.create_all()
    db_dir = app.config['UPLOAD_FOLDER']
    thumbnails_dir = os.path.join(db_dir, ".thumbnails")
    if (not os.path.exists(db_dir)) or (not os.path.exists(os.path.join(db_dir, ".thumbnails"))):
        os.makedirs(db_dir, exist_ok=True)
        os.makedirs(thumbnails_dir, exist_ok=True)

    # Setup the mosaic tile database
    pickle_to_hdf5(Path("cifar-10-batches-py"))
    app.run(debug=True)