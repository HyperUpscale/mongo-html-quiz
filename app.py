from flask import Flask, render_template, request, redirect, url_for, session
from pymongo import MongoClient
from bson.objectid import ObjectId
import base64
import os

# Create a Flask app instance
app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['your_database_name']
images = db['images']
results = db['results']
quizzes = db['quizzes']

MAX_FILE_SIZE = 1024 * 1024 * 10  # 10 MB
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Retrieve all quizzes from the database
def get_quizzes():
    return list(quizzes.find({}, {'_id': 0}))

# Upload an image to the database and associate it with a quiz
def upload_image(quiz_id, image_file, category, score):
    image_data = base64.b64encode(image_file.read()).decode('utf-8')
    return images.insert_one({'image_data': image_data, 'category': category, 'score': score, 'quiz_id': quiz_id}).inserted_id

# Retrieve images associated with a specific quiz from the database
def get_images_for_quiz(quiz_id, sort=None, skip=0, limit=0):
    query = {'quiz_id': quiz_id}
    projection = {'image_data': 1, '_id': 1, 'category': 1, 'score': 1}

    if sort:
        images_cursor = images.find(query, projection).sort(sort).skip(skip).limit(limit)
    else:
        images_cursor = images.find(query, projection).skip(skip).limit(limit)

    return list(images_cursor)

# Delete an image from the database
def delete_image(image_id, quiz_id):
    images.delete_one({'_id': ObjectId(image_id), 'quiz_id': quiz_id})

# Save a result image and its associated data to the database
def save_quiz_result_image(quiz_id, result_image, score_from, score_to, category, result_text):
    result_image_data = base64.b64encode(result_image.read()).decode('utf-8')
    results.insert_one({'image_data': result_image_data, 'score_from': score_from, 'score_to': score_to, 'result_text': result_text, 'category': category, 'quiz_id': quiz_id})

# Retrieve result images and their associated data for a specific quiz from the database
def get_quiz_result_images(quiz_id):
    return list(results.find({'quiz_id': quiz_id}, {'image_data': 1, 'score_from': 1, 'score_to': 1, 'result_text': 1, 'category': 1, '_id': 0}))

# Retrieve details for a specific page of images for a given quiz
def get_page_details(page_number, quiz_id):
    total_images = images.count_documents({'quiz_id': quiz_id})
    num_pages = (total_images + 2) // 3

    if page_number < 1 or page_number > num_pages:
        return None, None, None, None

    skip = (page_number - 1) * 3
    limit = 3

    current_images = get_images_for_quiz(quiz_id, sort=[('_id', -1)], skip=skip, limit=limit)
    top_images = get_images_for_quiz(quiz_id, sort=[('_id', -1)], limit=3)
    gallery = get_images_for_quiz(quiz_id, sort=[('score', 1)])

    return current_images, top_images, gallery, num_pages

# Routes
@app.route('/')
def index():
    quizzes = get_quizzes()
    current_quiz_id = session.get('current_quiz_id')
    return render_template('index.html', quizzes=quizzes, current_quiz_id=current_quiz_id)

@app.route('/upload_images/<string:quiz_id>', methods=['GET', 'POST'])
def upload_images(quiz_id):
    session['current_score'] = 0  # Reset the current score
    session['current_quiz_id'] = quiz_id  # Set the current_quiz_id

    if request.method == 'POST':
        # Check if a single image or result image was uploaded
        image_file = request.files.get('image')
        result_image = request.files.get('result_image')

        if image_file and allowed_file(image_file.filename):
            # Upload a single image for the quiz
            filename = secure_filename(image_file.filename)
            if image_file.content_length <= MAX_FILE_SIZE:
                try:
                    category = request.form['category'].strip()
                    score = int(request.form['score'])

                    # Validate category
                    if not category:
                        return "Category is required", 400
                    elif len(category) > 50:
                        return "Category must be less than 50 characters", 400

                    upload_image(quiz_id, image_file, category, score)

                except Exception as e:
                    app.logger.error(f"Error uploading image: {str(e)}")
                    return "Error uploading image", 500
            else:
                return "File size exceeds the limit", 413  # Request Entity Too Large

        elif result_image and allowed_file(result_image.filename):
            # Upload a result image
            if result_image.content_length <= MAX_FILE_SIZE:
                try:
                    score_from = int(request.form['score_from'])
                    score_to = int(request.form['score_to'])
                    category = request.form['category'].strip()
                    result_text = request.form['result_text'].strip()

                    # Validate category
                    if not category:
                        return "Category is required", 400
                    elif len(category) > 50:
                        return "Category must be less than 50 characters", 400

                    save_quiz_result_image(quiz_id, result_image, score_from, score_to, category, result_text)

                except Exception as e:
                    app.logger.error(f"Error uploading result image: {str(e)}")
                    return "Error uploading result image", 500
            else:
                return "File size exceeds the limit", 413  # Request Entity Too Large

        else:
            return "No file uploaded", 400  # Bad Request

    # Retrieve the gallery images from MongoDB for the current quiz
    gallery = get_images_for_quiz(quiz_id, sort=[('score', 1)])

    # Retrieve the result gallery images from MongoDB for the current quiz
    result_gallery = get_quiz_result_images(quiz_id)

    return render_template('edit_quiz.html', gallery=gallery, result_gallery=result_gallery, current_score=session.get('current_score', 0), current_quiz_id=quiz_id)

@app.route('/update_image/<image_id>', methods=['GET', 'POST'])
def update_image(image_id):
    quiz_id = request.args.get('quiz_id')

    if request.method == 'POST':
        # Get the updated parameters
        category = request.form['category'].strip()
        score = int(request.form['score'])

        # Validate category
        if not category:
            return "Category is required", 400
        elif len(category) > 50:
            return "Category must be less than 50 characters", 400

        # Update the image document in MongoDB
        images.update_one({'_id': ObjectId(image_id)}, {'$set': {'category': category, 'score': score}})

        return redirect(url_for('upload_images', quiz_id=quiz_id))

    # Retrieve the existing image document
    image_doc = images.find_one({'_id': ObjectId(image_id)})

    return render_template('update_image.html', image_doc=image_doc, quiz_id=quiz_id)

@app.route('/bulk_upload_images', methods=['POST'])
def bulk_upload_images():
    # Get the current_quiz_id from the query string or session
    current_quiz_id = request.form.get('quiz_id') or session.get('current_quiz_id')

    uploaded_files = request.files.getlist('images')
    default_score = int(request.form['score'])  # Get the score from the form

    for file in uploaded_files:
        if allowed_file(file.filename):
            filename = secure_filename(file.filename)
            if file.content_length <= MAX_FILE_SIZE:
                upload_image(current_quiz_id, file, None, default_score)
            else:
                app.logger.warning(f"File {filename} size exceeds the limit")
        else:
            app.logger.warning(f"Invalid file type for {file.filename}")

    # Redirect to the edit_quiz page for the current quiz after the bulk upload
    return redirect(url_for('upload_images', quiz_id=current_quiz_id))

# Quiz-related routes
@app.route('/quiz_setup', methods=['GET', 'POST'])
def quiz_setup():
    existing_quizzes = list(quizzes.find({}, {'_id': 0}))

    if request.method == 'POST':
        quiz_id = request.form['quiz_id'].strip()
        quiz_name = request.form['quiz_name'].strip()

        # Validate quiz_id and quiz_name
        if not quiz_id:
            return "Quiz ID is required", 400
        elif not quiz_name:
            return "Quiz name is required", 400

        # Check if the quiz_id already exists in the database
        existing_quiz = quizzes.find_one({'quiz_id': quiz_id})
        if existing_quiz:
            # Quiz ID already exists, handle the error
            error_message = f"Quiz ID '{quiz_id}' already exists. Please choose a different ID."
            return render_template('quiz_setup.html', quizzes=existing_quizzes, error_message=error_message)

        # Quiz ID is unique, proceed with creating the new quiz
        quizzes.insert_one({'quiz_id': quiz_id, 'quiz_name': quiz_name})
        return redirect(url_for('quiz_setup'))

    return render_template('quiz_setup.html', quizzes=existing_quizzes)

@app.route('/edit_quiz/<string:quiz_id>', methods=['GET', 'POST'])
def edit_quiz(quiz_id):
    quiz = quizzes.find_one({'quiz_id': quiz_id}, {'_id': 0})

    # Handle image upload
    if 'image' in request.files:
        image_file = request.files['image']
        if image_file and allowed_file(image_file.filename):
            filename = secure_filename(image_file.filename)
            if image_file.content_length <= MAX_FILE_SIZE:
                category = request.form['category'].strip()
                score = int(request.form['score'])

                # Validate category
                if not category:
                    return "Category is required", 400
                elif len(category) > 50:
                    return "Category must be less than 50 characters", 400

                upload_image(quiz_id, image_file, category, score)
            else:
                return "File size exceeds the limit", 413  # Request Entity Too Large
        else:
            return "Invalid file type", 415  # Unsupported Media Type

    # Handle result image upload
    if 'result_image' in request.files:
        result_image = request.files['result_image']
        if result_image and allowed_file(result_image.filename):
            score_from = int(request.form.get('score_from', 0))
            score_to = int(request.form.get('score_to', 0))
            category = request.form.get('category', '').strip()
            result_text = request.form['result_text'].strip()

            # Save the result image to the database
            save_quiz_result_image(quiz_id, result_image, score_from, score_to, category, result_text)

    if request.method == 'POST':
        # Handle the form submission for editing the quiz
        quiz_name = request.form['quiz_name'].strip()

        # Validate quiz_name
        if not quiz_name:
            return "Quiz name is required", 400

        quizzes.update_one({'quiz_id': quiz_id}, {'$set': {'quiz_name': quiz_name}})
        return redirect(url_for('index'))

    # Retrieve the images for the current quiz
    gallery = list(images.find({'quiz_id': quiz_id}, {'image_data': 1, '_id': 1, 'category': 1, 'score': 1, 'quiz_id': 1}).sort('score', 1))

    # Retrieve the result images for the current quiz
    result_gallery = get_quiz_result_images(quiz_id)

    return render_template('edit_quiz.html', quiz=quiz, current_quiz_id=quiz_id, gallery=gallery, result_gallery=result_gallery)

# Image-related routes
@app.route('/delete_quiz/<string:quiz_id>', methods=['GET'])
def delete_quiz(quiz_id):
    # Delete the quiz with the given quiz_id from MongoDB
    quizzes.delete_one({'quiz_id': quiz_id})
    images.delete_many({'quiz_id': quiz_id})
    return redirect(url_for('index'))

@app.route('/delete_image/', methods=['GET'])
def delete_image():
    image_id = request.args.get('image_id')
    quiz_id = request.args.get('quiz_id')
    if image_id == '0':
        # Delete the entire quiz and its associated images
        images.delete_many({'quiz_id': quiz_id})
        quizzes.delete_one({'quiz_id': quiz_id})
    else:
        if quiz_id:
            # Delete the image with the given image_id and quiz_id from MongoDB
            delete_image(image_id, quiz_id)
        return redirect(url_for('upload_images', quiz_id=quiz_id))
    return redirect(url_for('index'))

# Result-related routes
@app.route('/quiz_result', methods=['GET', 'POST'])
def quiz_result():
    quiz_id = request.args.get('quiz_id') or session.get('current_quiz_id')

    # Retrieve the result images and texts from the database for the current quiz
    result_gallery = get_quiz_result_images(quiz_id)

    # Find the result image based on the current score for the current quiz
    current_score = session.get('current_score', 0)
    result_doc = results.find_one({'quiz_id': quiz_id, 'score_from': {'$lte': current_score}, 'score_to': {'$gte': current_score}}, {'image_data': 1, 'result_text': 1, '_id': 0})

    # Calculate the number of pages
    total_images = images.count_documents({'quiz_id': quiz_id})
    num_pages = (total_images + 2) // 3  # Round up to the nearest integer

    return render_template('quiz_result.html', result_doc=result_doc, result_gallery=result_gallery, current_quiz_id=quiz_id, current_score=current_score, num_pages=num_pages)


@app.route('/reset', methods=['GET'])
def reset():
    session.pop('current_score', None)
    session.pop('current_quiz_id', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.secret_key = 'your_secret_key'
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=True)