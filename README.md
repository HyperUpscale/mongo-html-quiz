# mongo-html-quiz
Test mongo quiz


this project is a web application built using Flask, a Python web framework, and MongoDB, a NoSQL database. The application allows users to create and manage quizzes, upload images associated with each quiz, and display the quiz results based on the user's score.

Project Requirements:
    Flask Framework: The application is built using Flask, a lightweight Python web framework that provides the necessary tools for creating web applications, handling HTTP requests, rendering templates, and managing application routing.
    MongoDB Integration: The application utilizes MongoDB, a NoSQL document-based database, to store and retrieve data related to quizzes, images, and result images. The pymongo library is used for interacting with the MongoDB database.
    User Interface: The application provides a user interface built with HTML templates and rendered using Flask's template engine (Jinja2). The HTML templates define the structure and layout of the various pages, such as the index page, quiz setup page, image upload page, quiz entry page, and quiz result page.
    Quiz Management:
        Quiz Creation: Users can create new quizzes by providing a unique quiz ID and a quiz name.
        Quiz Editing: Existing quizzes can be edited by updating the quiz name.
        Quiz Deletion: Quizzes can be deleted, which also removes all associated images.
        Quiz List: The application displays a list of existing quizzes on the index page, allowing users to navigate to specific quizzes.
    Image Upload:
        Single Image Upload: Users can upload individual images for a selected quiz, providing a category and a score for each image.
        Bulk Image Upload: The application supports bulk uploading of multiple images for a selected quiz, with a default score assigned to the entire batch.
        Image Gallery: A gallery page displays all uploaded images for the selected quiz, allowing users to view, edit, and delete individual images.
    Quiz Entry:
        Image Selection: The quiz entry page displays three images at a time from the selected quiz, allowing users to navigate through the images page by page.
        Score Calculation: As users select images, the application calculates and updates the current score based on the scores associated with the selected images.
    Quiz Result:
        Result Image Upload: Users can upload a result image for a specific quiz, specifying the score range, category, and result text associated with the image.
        Result Image Gallery: The quiz result page displays all uploaded result images for the selected quiz, along with their corresponding score ranges and result texts.
        Final Result Display: Based on the user's current score, the application displays the appropriate result image and result text.
    Database Integration:
        Quiz Data Storage: The application stores quiz data, including quiz IDs, quiz names, and associated images, in the MongoDB database.
        Image Data Storage: Image data is stored in the database as base64-encoded strings, along with their respective categories and scores.
        Result Image Data Storage: Result images are stored in the database, along with their associated score ranges, categories, and result texts.
    Routing and URL Handling: Flask's routing mechanisms are utilized to map URLs to corresponding Python functions, enabling navigation between different pages and handling various HTTP requests (GET, POST) for data retrieval and submission.
    Form Handling: The application handles form submissions for quiz creation, image uploads, and result image uploads, ensuring proper data validation and processing.
    Session Management: Flask's session management is used to track the current score and the currently selected quiz across multiple pages.
    Error Handling: The application includes basic error handling mechanisms, such as handling file uploads exceeding the maximum file size or uploading unsupported file types.
    Logging: The application implements logging functionality using Python's logging module, allowing for tracking and debugging application events.

mongo11-25/
├── app/
│   ├── __init__.py
│   ├── routes.py
│   ├── forms.py
│   ├── models.py
│   ├── utils.py
│   └── templates/
│       ├── base.html
│       ├── bulk_image_upload.html
│       ├── index.html
│       ├── create_quiz.html
│       ├── delete_quiz.html
│       ├── edit_quiz.html
│       ├── quiz_images.html
│       ├── quiz_entry.html
│       ├── quiz_result.html
│       ├── result_image_upload.html
│       └── result_images.html
├── config.py
├── requirements.txt
└── run.py


    app/__init__.py: Initialize the Flask application and MongoDB connection.
    app/routes.py: Define the application routes and corresponding views.
    app/forms.py: Define the forms for user input (e.g., quiz creation, image upload).
    app/models.py: Define the data models for quizzes, images, and result images.
    app/utils.py: Utility functions for image handling, score calculation, and other helper methods.
    app/templates/: Directory for storing HTML templates.
    config.py: Configuration settings for the application and MongoDB.
    run.py: Entry point for running the Flask application.

Implement the Flask application code:

    In app/__init__.py, initialize the Flask application and MongoDB connection.
    In app/routes.py, define the routes and corresponding views for handling different aspects of the application, such as creating quizzes, uploading images, displaying quiz entries, and showing quiz results.
    In app/forms.py, define the necessary forms using Flask-WTF for user input validation.
    In app/models.py, define the data models for quizzes, images, and result images using MongoDB's document structure.
    In app/utils.py, implement utility functions for image handling, score calculation, and other helper methods.
    In app/templates/, create the HTML templates for each page of the application using Jinja2 templating engine and Flask's rendering capabilities.
    In config.py, define the configuration settings for the Flask application and MongoDB connection details.
    In run.py, create the entry point for running the Flask application.
ADDITIONAL Requirements:
- Buttons to edit, delete and start, as well as a thumbnail for each of the available quizzes on the index page.
- The pages before the result page are based on the images in the gallery 
- uploading result images have to include the range of score, based on which it will be displaied at the end of the quiz it belongs to. So when uploaded we need to specify the integer of the start values and end values the result imgage will be shown.
- a single matching score result image will be shown as the last page of each quiz. the other place they can be seen is in edit quiz view, where all images for the quiz shoulb de seen in a gallery view.
- the images should include text: the regular quiz images and the result image. The difference for the result images is that their text has to be html format supportive, while the others just plain text.
- the 3 images to choose from should be clickable and that would result as a score increase based on the image score AND moving to the next 3 images from the gallery.
- To display the gallery in multi rows images as thumbnails 
- Seperate button to uplead result images


THE MISSING CODE FOR EACH FILE OR FILES TO COMPLETE THE PROJECT CODE to make the project fully functional,
