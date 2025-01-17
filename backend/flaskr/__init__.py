
import json

import os
from unicodedata import category
from urllib import response
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category, db

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    Set up CORS. Allow '*' for origins. Delete the sample route
    after completing the TODOs
    """
    CORS(app)
    """
    DONE: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-typle,Authorization,true"
        )

        response.headers.add(
            "Access-Control-Allow-Methods", "GET,POST,PATCH,PUT,DELETE,OPTIONS"
        )
        return response
    """
    DONE:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories')
    def get_categories():
        try:
            categories = Category.query.order_by(Category.id).all()
            categoryObject = {}
            for category in categories:
                categoryObject[category.id] = category.type
            if categories is None:
                abort(404)
            return jsonify({
                'success': True,
                'categories': categoryObject,
                'total_category': len(Category.query.all())
            })
        except:
            abort(422)
    """
    DONE
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the
    screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    def paginate_question(request, selection):
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE

        questions = [question.format() for question in selection]
        current_questions = questions[start:end]
        return current_questions

    @app.route('/questions')
    def get_questions():
        try:
            # get all questions
            all_questions = Question.query.order_by(Question.id).all()
            current_questions = paginate_question(request, all_questions)
            # get all categories
            categories = Category.query.order_by(Category.id).all()
            categoriesDict = {}
            for category in categories:
                categoriesDict[category.id] = category.type

            if len(current_questions) == 0:
                abort(404)

            return jsonify({
                'success': True,
                'questions': current_questions,
                'total_questions': len(Question.query.all()),
                'categories': categoriesDict
            })
        except:
            abort(404)
    """
    DONE:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question,
    the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.filter(Question.id
                == question_id).one_or_none()

            if question is None:
                abort(404)

            question.delete()
            all_question = Question.query.order_by(Question.id).all()
            current_question = paginate_question(request, all_question)

            return jsonify({
                'success': True,
                'deleted': question_id,
                'total_question': len(Question.query.all()),
                'questions': current_question
            })
        except:
            abort(422)
    """
    DONE:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear
    at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route('/questions', methods=['POST'])
    def create_new_questions():
        body = request.get_json()

        new_question = body.get('question', None)
        new_answer = body.get('answer', None)
        category = body.get('category', None)
        difficulty = body.get('difficulty', None)

        if new_question is None and new_answer is None and category is None and difficulty is None:
            abort(400)

        try:
            question = Question(question=new_question, answer=new_answer, category=category, difficulty=difficulty)
            question.insert()

            all_question = Question.query.order_by(Question.id).all()
            current_question = paginate_question(request, all_question)
            return ({
                'success': True,
                'created': question.id,
                'questions': current_question,
                'total_question': len(Question.query.all())
            })
        except:
            abort(405)
    """
    DONE:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route('/questions/search', methods=['POST'])
    def search_question():
        body = request.get_json()

        word = body.get('searchTerm', None)
        try: 
            search_list = []
            all_question = Question.query.all()
            for question in all_question:
                if (question.question.lower().find(word.lower()) != -1):
                    search_list.append(question.format())

            # current_question = paginate_question(request, search_list)
            if search_list is None:
                abort(404)
            return jsonify({
                'success': True,
                'questions': search_list,
                'total_questions': len(search_list),
                
            })
        except:
            abort(422)

    """
    DONE:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<int:category_id>/questions')
    def get_questions_based_on_category(category_id):

        try:
            questions_in_category = Question.query.filter_by(category = category_id).all()
            category = Category.query.filter(Category.id == category_id).one_or_none()

            if questions_in_category is None and category is None:
                abort(404)

            list_questions = [questions.format() for questions in questions_in_category]
            return jsonify({
                'success': True,
                'questions': list_questions,
                'current_category': category.type,
                'total_questions': len(list_questions)
            })
        except:
            abort(422)

    """
    DONE:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route('/quizzes', methods=['POST'])
    def play_quiz():
        body = request.get_json()
        question_category = body.get('quiz_category', None)
        previous_question = body.get('previous_questions', None)
        if question_category is None and previous_question is None:
            abort(400)
        try:
            if (question_category['id'] == 0):
                questions = Question.query.filter(Question.id.not_in(previous_question)).all()
            else:
                questions = Question.query.filter_by(
                    category=question_category['id']).filter(Question.id.not_in(previous_question)).all()
            
            for question in questions:
                if question.id in previous_question:
                    questions.remove(question)

            if len(questions) > 0:
                nextQuestion = questions[random.randint(0, len(questions)-1)]
                
                return jsonify({
                    'success': True,
                    'question': {
                        "answer": nextQuestion.answer,
                        "category": nextQuestion.category,
                        "difficulty": nextQuestion.difficulty,
                        "id": nextQuestion.id,
                        "question": nextQuestion.question
                    },
                })
            else:
                return jsonify({
                   'success': True,
                })
        except:
            abort(404)
    """
    DONE:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'Resource not Found'
        }), 404

    @app.errorhandler(422)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'Unprocessable Entity'
        }), 422

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            'success': False,
            'error':405,
            'message': 'method not allowed'
        }), 405
        
    @app.errorhandler(400)
    def method_not_allowed(error):
        return jsonify({
            'success': False,
            'error':400,
            'message': 'Bad Request'
        }), 400
    
    @app.errorhandler(500)
    def server_error(error):
        return jsonify({
            'success': False,
            'error': 500,
            'message': 'Internal Server Error'
        }), 500

    return app