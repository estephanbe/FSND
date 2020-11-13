import json
import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
import sys

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginated_questions(request, questions):
  page = int(request.args.get('page', 1))
  start = (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE

  return questions[start:end]

  

  return 


def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  cors = CORS(app, resources={r"/*": {"origins": "*"}})
  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')

    return response

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories')
  def get_cats():
    cats = []
    formated_cats = []
    try:
      cats = Category.query.all()
    except: 
      abort(404)

    if 0 < len(cats):
      formated_cats = {category.id: category.type for category in cats}


    return jsonify({
      "categories": formated_cats
    })

  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions')
  def get_questions():
    cats = []
    questions = []
    formatted_categories = {}
    try:
      cats = Category.query.all()
    except: 
      abort(404)

    if 0 < len(cats):
      formatted_categories = {category.id: category.type for category in cats}
    
    try:
      questions = Question.query.order_by(Question.id).all()
    except: 
      abort(404)
    
    paginated_qs = paginated_questions(request, questions)
    if 0 == len(paginated_qs):
      abort(404)

    formated = [q.format() for q in paginated_qs]
    
    return jsonify({
      "questions": formated,
      "total_questions": len(questions),
      "current_category": None,
      "categories": formatted_categories
    })

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:id>', methods=["DELETE"])
  def delete_question(id):
    question = Question.query.filter(Question.id == id).one_or_none()
    
    if question is None:
      abort(422)
    try:
      question.delete()
    except:
      abort(422)

    return jsonify({
      "success": True,
      "deleted": id
    })

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questions', methods=["POST"])
  def handle_post_requestes():
    body = {}
    data = request.get_json()
    
    # Check if the request was sent empty and abort it.
    if data is None or not len(data):
      abort(422)
    
    if "searchTerm" in data:
      try:
        questions = Question.query.filter(Question.question.ilike("%{}%".format(data["searchTerm"])))
        questions = [q.format() for q in questions]
        body = {
          "questions": questions,
          "totalQuestions": len(questions),
          "currentCategory": None
        }
      except:
        print(sys.exc_info())
        abort(404)
    elif "question" in data and "answer" in data and "difficulty" in data and "category" in data:
      question = Question(
        question=data['question'],
        answer=data['answer'],
        difficulty=int(data['difficulty']),
        category=int(data['category']),
      )
      try:
        question.insert()
        body = {
          "success": True,
          "question_id": question.id
        }
      except:
        abort(422)
    else:
      abort(422)
      

    return jsonify(body)

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:cat_id>/questions')
  def get_by_cat(cat_id):
    questions = []
    try:
      questions = Question.query.filter(Question.category == '{}'.format(cat_id)).all()
    except: 
      print(sys.exc_info())
      abort(404)
    
    if 0 == len(questions):
      abort(404)

    formated = [q.format() for q in questions]
    
    return jsonify({
      "questions": formated,
      "total_questions": len(questions),
      "current_category": cat_id,
    })


  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes', methods=["POST"])
  def generate_quize():
    body = {}
    data = request.get_json()
    
    # Check if the request was sent empty and abort it.
    if data is None or not len(data):
      abort(422)

    # Check if the request doesn't have the arguments and abort if not.
    if "previous_questions" not in data and "quiz_category" not in data:
      abort(422)

    questions = []
    previous_questions = []

    try:
      quiz_cat_id = int(data["quiz_category"]["id"])
      previous_questions = data["previous_questions"]
      if quiz_cat_id:
        questions = Question.query.filter(Question.category == quiz_cat_id).all()
      else:
        questions = Question.query.all()
    except:
      abort(422)

    formated_questions = [q.format() for q in questions]
    eligible_questions = []
    for q in formated_questions:
      if q["id"] not in previous_questions:
        eligible_questions.append(q["id"])
    choosen_question_id = random.choice(eligible_questions)
    choosen_question = Question.query.filter(Question.id == choosen_question_id).one_or_none()
    body = {
      "question": choosen_question.format()
    }

    return jsonify(body)

  '''
  Create new category endpoint
  '''
  @app.route('/category', methods=["POST"])
  def create_cat():
    body = {
      "success": False
    }
    data = request.get_json()
    
    # Check if the request was sent empty and abort it.
    if data is None or not len(data):
      abort(422)

    # Check if the request doesn't have the arguments and abort if not.
    if "cat_type" not in data:
      abort(422)
    
    cat = Category(type=data["cat_type"])
    try:
      cat.insert()
      body["success"] = True
    except:
      abort(422)


    return jsonify(body)


  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      "success": False,
      "error": 404,
      "message": "resource was not found"
    }), 404

  @app.errorhandler(422)
  def not_found(error):
    return jsonify({
      "success": False,
      "error": 422,
      "message": "Unprocessable Entity"
    }), 422
  
  return app

    