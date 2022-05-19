import os
import random

from flask import Flask, render_template, url_for, flash, request, redirect
from helper import classify_image, save_to_disk, delete_from_disk
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

UPLOAD_FOLDER = '/home/elewis/Projects/shopify/shopify-image-repo/front/static/server_db/sources'
ALLOWED_EXTENSIONS = set(['png', 'jpeg', 'jpg'])

# TODO: If not exists create database folders

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'

db = SQLAlchemy(app)
#db.create_all()

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tags = db.Column(db.String(200), nullable=True)
    fn = db.Column(db.String(200), nullable=False)
    filepath = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Task {self.id}>'

@app.route('/')
def index():
    entries = Todo.query.order_by(Todo.date_created).all()
    return render_template('index.html', entries=entries)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
        if img and allowed_file(img.filename):
            # TODO: Process file to lmdb or whatever and save it to the database here
            # Save file
            filename = secure_filename(img.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            img.save(filepath)
            
            # Save thumbnail to disk and process computer vision
            best_guesses = save_to_disk(app.config['UPLOAD_FOLDER'], filename)
            print(" ".join([x[1] for x in best_guesses]))
            threshold = 0.33
            best_guess = best_guesses[0][1]
            tags = [ guess[1] for guess in best_guesses if guess[-1] > threshold]
            
            # Add to database
            new_entry = Todo(tags=''.join(tags), fn=filename, filepath=filepath)
            try:
                db.session.add(new_entry)
                db.session.commit()
            except Exception as e:
                print(e)
                return "ERROR WITH DB FUNCS"
            return redirect('/')
        else:
            flash('File must be a lossless format.')
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
    entry_to_delete = Todo.query.get_or_404(id)

    delete_from_disk(entry_to_delete.filepath, entry_to_delete.fn)
    try:
        db.session.delete(entry_to_delete)
        db.session.commit()
        return redirect('/')
    except Exception as e:
        print(e)
        return 'ERROR ON DELETE'

from flask import send_from_directory

@app.route('/view/<int:id>')
def view(id):
    entry_to_view = Todo.query.get_or_404(id)

    return render_template("view.html", entry = entry_to_view)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

if __name__ == "__main__":
    app.secret_key = "super secret key"
    app.run(debug=True)