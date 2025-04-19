import os
from flask import Flask, render_template, request, send_from_directory
from werkzeug.utils import secure_filename
from pymongo import MongoClient

UPLOAD_FOLDER_IMAGES = 'static/uploads/'
UPLOAD_FOLDER_RESUMES = 'static/resumes/'
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg'}
ALLOWED_PDF_EXTENSIONS = {'pdf'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER_IMAGES'] = UPLOAD_FOLDER_IMAGES
app.config['UPLOAD_FOLDER_RESUMES'] = UPLOAD_FOLDER_RESUMES

import os
from flask import Flask, render_template, request, send_from_directory
from werkzeug.utils import secure_filename
from pymongo import MongoClient

UPLOAD_FOLDER_IMAGES = 'static/uploads/'
UPLOAD_FOLDER_RESUMES = 'static/resumes/'
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg'}
ALLOWED_PDF_EXTENSIONS = {'pdf'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER_IMAGES'] = UPLOAD_FOLDER_IMAGES
app.config['UPLOAD_FOLDER_RESUMES'] = UPLOAD_FOLDER_RESUMES

mongo_uri = os.environ.get("MONGODB_URI", "mongodb+srv://iram15:UNnr3JpQnPp9NeeX@cluster0.ten3jrd.mongodb.net/")
client = MongoClient(mongo_uri)
db = client["portfolio_builder"]
users = db["portfolios"]
db = client["portfolio_builder"]
users = db["portfolios"]

def allowed_file(filename, allowed_set):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_set

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form["name"]
        bio = request.form["bio"]
        skills = request.form["skills"].split(",")
        # projects = request.form["projects"].split(",")
        email = request.form["email"]

        image_file = request.files["profile"]
        image_filename = None
        if image_file and allowed_file(image_file.filename, ALLOWED_IMAGE_EXTENSIONS):
            image_filename = secure_filename(image_file.filename)
            image_file.save(os.path.join(app.config['UPLOAD_FOLDER_IMAGES'], image_filename))

        resume_file = request.files["resume"]
        resume_filename = None
        if resume_file and allowed_file(resume_file.filename, ALLOWED_PDF_EXTENSIONS):
            resume_filename = secure_filename(resume_file.filename)
            resume_file.save(os.path.join(app.config['UPLOAD_FOLDER_RESUMES'], resume_filename))

        # Handle multiple projects with name, link, and image
        project_names = request.form.getlist("project_names[]")
        project_links = request.form.getlist("project_links[]")
        project_images_files = request.files.getlist("project_images[]")

        projects = []
        for i in range(len(project_names)):
            proj_image_filename = None
            if i < len(project_images_files):
                proj_image_file = project_images_files[i]
                if proj_image_file and allowed_file(proj_image_file.filename, ALLOWED_IMAGE_EXTENSIONS):
                    proj_image_filename = secure_filename(proj_image_file.filename)
                    proj_image_file.save(os.path.join(app.config['UPLOAD_FOLDER_IMAGES'], proj_image_filename))
            projects.append({
                "name": project_names[i],
                "link": project_links[i],
                "image": proj_image_filename
            })

        data = {
            "name": name,
            "bio": bio,
            "skills": skills,
            "projects": projects,
            "email": email,
            "image": image_filename,
            "resume": resume_filename
        }
        users.insert_one(data)
        return render_template("preview.html", data=data)

    return render_template("index.html")

@app.route('/resumes/<filename>')
def download_resume(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER_RESUMES'], filename)

if __name__ == "__main__":
    app.run(debug=True)
