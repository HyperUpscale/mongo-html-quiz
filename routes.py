import base64
import io
from bson import ObjectId
from flask import render_template, redirect, url_for, flash, session, request
from app import app, mongo
from app.forms import QuizForm, ImageUploadForm, ResultImageUploadForm
from app.models import Quiz, Image, ResultImage
from app.utils import get_image_data

@app.route('/')
@app.route('/index')
def index():
    quizzes = mongo.db.quizzes.find()
    return render_template('index.html', quizzes=quizzes)

@app.route('/create_quiz', methods=['GET', 'POST'])
def create_quiz():
    form = QuizForm()
    if form.validate_on_submit():
        quiz = Quiz(quiz_id=form.quiz_id.data, name=form.name.data)
        mongo.db.quizzes.insert_one(quiz.to_dict())
        flash('Quiz created successfully!', 'success')
        return redirect(url_for('index'))
    return render_template('create_quiz.html', form=form)

@app.route('/quiz_setup/<quiz_id>', methods=['GET'])
def quiz_setup(quiz_id):
    quiz = mongo.db.quizzes.find_one({'quiz_id': quiz_id})
    if quiz is None:
        flash('Quiz not found', 'error')
        return redirect(url_for('index'))

    return render_template('quiz_setup.html', quiz=quiz)

@app.route('/edit_quiz/<quiz_id>', methods=['GET', 'POST'])
def edit_quiz(quiz_id):
    quiz = mongo.db.quizzes.find_one({'quiz_id': quiz_id})
    if not quiz:
        flash('Quiz not found', 'error')
        return redirect(url_for('index'))

    gallery = list(mongo.db.images.find({'quiz_id': quiz_id}))
    result_gallery = list(mongo.db.result_images.find({'quiz_id': quiz_id}))

    if request.method == 'POST':
        new_name = request.form.get('quiz_name')
        if new_name:
            mongo.db.quizzes.update_one({'quiz_id': quiz_id}, {'$set': {'name': new_name}})
            flash('Quiz updated successfully!', 'success')
            quiz = mongo.db.quizzes.find_one({'quiz_id': quiz_id})

    return render_template('edit_quiz.html', quiz=quiz, gallery=gallery, result_gallery=result_gallery)


@app.route('/delete_quiz/<quiz_id>', methods=['GET', 'POST'])
def delete_quiz(quiz_id):
    quiz = mongo.db.quizzes.find_one({'quiz_id': quiz_id})
    if not quiz:
        flash('Quiz not found', 'error')
        return redirect(url_for('index'))

    if request.method == 'POST':
        mongo.db.quizzes.delete_one({'quiz_id': quiz_id})
        mongo.db.images.delete_many({'quiz_id': quiz_id})
        mongo.db.result_images.delete_many({'quiz_id': quiz_id})
        flash('Quiz and associated images deleted successfully!', 'success')
        return redirect(url_for('index'))

    return render_template('delete_quiz.html', quiz=quiz)
    
        
@app.route('/quiz_images/<quiz_id>', methods=['GET', 'POST'])
def quiz_images(quiz_id):
    quiz = mongo.db.quizzes.find_one({'quiz_id': quiz_id})
    if quiz is None:
        flash('Quiz not found', 'error')
        return redirect(url_for('index'))

    images = mongo.db.images.find({'quiz_id': quiz_id})
    form = ImageUploadForm()
    if form.validate_on_submit():
        if form.image.data:
            image_data = base64.b64encode(form.image.data.read()).decode('utf-8')
            image = Image(quiz_id=quiz_id, category=form.category.data, score=form.score.data, image_data=image_data)
            mongo.db.images.insert_one(image.to_dict())
            flash('Image uploaded successfully!', 'success')
        else:
            flash('No image selected', 'error')
    return render_template('quiz_images.html', quiz=quiz, images=images, form=form)

@app.route('/bulk_image_upload/<quiz_id>', methods=['GET', 'POST'])
def bulk_image_upload(quiz_id):
    quiz = mongo.db.quizzes.find_one({'quiz_id': quiz_id})
    if quiz is None:
        flash('Quiz not found', 'error')
        return redirect(url_for('index'))

    if request.method == 'POST':
        files = request.files.getlist('images')
        default_score = request.form.get('default_score', 0)
        for file in files:
            image_data = file.read()
            encoded_image_data = base64.b64encode(image_data).decode('utf-8')
            image = Image(quiz_id=quiz_id, category='Bulk Upload', score=int(default_score), image_data=encoded_image_data)
            mongo.db.images.insert_one(image.to_dict())
        flash('Images uploaded successfully!', 'success')
        return redirect(url_for('quiz_images', quiz_id=quiz_id))

    return render_template('bulk_image_upload.html', quiz=quiz)

@app.route('/quiz_entry/<quiz_id>', methods=['GET', 'POST'])
def quiz_entry(quiz_id):
    quiz = mongo.db.quizzes.find_one({'quiz_id': quiz_id})
    if quiz is None:
        flash('Quiz not found', 'error')
        return redirect(url_for('index'))

    images = list(mongo.db.images.find({'quiz_id': quiz_id, 'category': {'$ne': 'Result Image'}}))
    if not images:
        flash('No images found for this quiz', 'error')
        return redirect(url_for('quiz_images', quiz_id=quiz_id))

    if 'current_score' not in session:
        session['current_score'] = 0

    page = int(request.args.get('page', 0))
    start = page * 3
    end = start + 3
    current_images = images[start:end]

    if request.method == 'POST':
        selected_image_id = request.form.get('image_id')
        if selected_image_id:
            image = mongo.db.images.find_one({'_id': ObjectId(selected_image_id)})
            if image is not None:
                session['current_score'] += image['score']

        if end >= len(images):
            return redirect(url_for('quiz_result', quiz_id=quiz_id))
        else:
            return redirect(url_for('quiz_entry', quiz_id=quiz_id, page=page + 1))

    return render_template('quiz_entry.html', quiz=quiz, images=current_images, current_score=session['current_score'], page=page)

@app.route('/result_image_upload/<quiz_id>', methods=['GET', 'POST'])
def result_image_upload(quiz_id):
    quiz = mongo.db.quizzes.find_one({'quiz_id': quiz_id})
    if quiz is None:
        flash('Quiz not found', 'error')
        return redirect(url_for('index'))

    form = ResultImageUploadForm()
    if form.validate_on_submit():
        image_data = base64.b64encode(form.image.data.read()).decode('utf-8')
        score_start, score_end = map(int, form.score_range.data.split('-'))
        result_image = ResultImage(
            quiz_id=quiz_id,
            category=form.category.data,
            score_start=score_start,
            score_end=score_end,
            result_text=form.result_text.data,
            image_data=image_data
        )
        mongo.db.result_images.insert_one(result_image.to_dict())
        flash('Result image uploaded successfully!', 'success')
        return redirect(url_for('result_images', quiz_id=quiz_id))

    return render_template('result_image_upload.html', form=form, quiz=quiz)

@app.route('/result_images/<quiz_id>', methods=['GET'])
def result_images(quiz_id):
    quiz = mongo.db.quizzes.find_one({'quiz_id': quiz_id})
    if quiz is None:
        flash('Quiz not found', 'error')
        return redirect(url_for('index'))

    result_images = mongo.db.result_images.find({'quiz_id': quiz_id})
    return render_template('result_images.html', quiz=quiz, result_images=result_images)

@app.route('/quiz_result/<quiz_id>', methods=['GET'])
def quiz_result(quiz_id):
    quiz = mongo.db.quizzes.find_one({'quiz_id': quiz_id})
    if quiz is None:
        flash('Quiz not found', 'error')
        return redirect(url_for('index'))

    current_score = session.get('current_score', 0)
    result_image = mongo.db.result_images.find_one({
        'quiz_id': quiz_id,
        'score_range': {'$regex': f'^{current_score}-'}
    })

    if result_image:
        image_data = get_image_data(result_image['image_data'])
        result_text = result_image['result_text']
    else:
        image_data = None
        result_text = 'No result image found for your score.'

    return render_template('quiz_result.html', quiz=quiz, image_data=image_data, result_text=result_text, current_score=current_score)

