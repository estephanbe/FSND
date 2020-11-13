import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}:{}@{}/{}".format('postgres', 'root', 'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_general_404_error(self):
        res = self.client().get('/lksjfdlkd')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['error'], 404)
        self.assertEqual(data['message'], 'resource was not found')
        self.assertFalse(data['success'])


    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['categories'])
        self.assertGreater(len(data['categories']), 0)

    def test_get_questions_with_valid_page_number(self):
        res = self.client().get('/questions?page=1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)

        self.assertTrue(data["categories"])
        self.assertTrue(data["questions"])
        self.assertTrue(data["total_questions"])

        self.assertIsNone(data["current_category"])

        self.assertGreater(len(data["questions"]), 0)
        self.assertGreater(len(data["categories"]), 0)
        self.assertGreater(data["total_questions"], 0)

    def test_get_questions_with_invalid_page_number(self):
        res = self.client().get('/questions?page=999')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['error'], 404)
        self.assertEqual(data['message'], 'resource was not found')
        self.assertFalse(data['success'])

    # def test_delete_question_with_valid_id(self):
    #     res = self.client().delete('/questions/2')
    #     data = json.loads(res.data)
    #     deleted_question = Question.query.filter(Question.id == 2).one_or_none()

    #     self.assertEqual(res.status_code, 200)
    #     self.assertTrue(data['success'])
    #     self.assertTrue(data['deleted'])
    #     self.assertIsNone(deleted_question)
    
    def test_delete_question_with_invalid_id(self):
        res = self.client().delete('/questions/53435735435')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['error'], 422)
        self.assertEqual(data['message'], 'Unprocessable Entity')
        self.assertFalse(data['success'])
    
    def test_create_new_question(self):
        res = self.client().post('/questions', json={"question": "new question", "answer": "new answer", "difficulty": "1", "category": "5"})
        data = json.loads(res.data)
        new_question = Question.query.filter(Question.id == data["question_id"]).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(data['question_id'])
        self.assertIsNotNone(new_question)

    def test_create_new_question_without_question(self):
        res = self.client().post('/questions', json={"answer": "new answer", "difficulty": "1", "category": "5"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['error'], 422)
        self.assertEqual(data['message'], 'Unprocessable Entity')
        self.assertFalse(data['success'])
    
    def test_create_new_question_without_answer(self):
        res = self.client().post('/questions', json={"question": "new question", "difficulty": "1", "category": "5"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['error'], 422)
        self.assertEqual(data['message'], 'Unprocessable Entity')
        self.assertFalse(data['success'])

    def test_create_new_question_without_difficulty(self):
        res = self.client().post('/questions', json={"question": "new question", "answer": "new answer", "category": "5"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['error'], 422)
        self.assertEqual(data['message'], 'Unprocessable Entity')
        self.assertFalse(data['success'])

    def test_create_new_question_without_category(self):
        res = self.client().post('/questions', json={"question": "new question", "answer": "new answer", "difficulty": "1"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['error'], 422)
        self.assertEqual(data['message'], 'Unprocessable Entity')
        self.assertFalse(data['success'])
    
    def test_create_new_question_without_data(self):
        res = self.client().post('/questions', json={})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['error'], 422)
        self.assertEqual(data['message'], 'Unprocessable Entity')
        self.assertFalse(data['success'])

    def test_search_for_term(self):
        res = self.client().post('/questions', json={"searchTerm": "M"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['questions'])
        self.assertTrue(data['totalQuestions'])
        self.assertIsNone(data['currentCategory'])
    
    def test_search_for_term_not_found(self):
        res = self.client().post('/questions', json={"searchTerm": "as3d2f1as3df57a4sd3f2a1sdf35a7sd4f3"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertIsNone(data['currentCategory'])
        self.assertEqual(len(data['questions']), 0)
        self.assertEqual(data['totalQuestions'], 0)

    def test_get_questions_by_category(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)

        self.assertTrue(data["questions"])
        self.assertTrue(data["total_questions"])
        self.assertTrue(data["current_category"])

        self.assertGreater(len(data["questions"]), 0)
        self.assertGreater(data["total_questions"], 0)

    def test_get_questions_by_category_not_found(self):
        res = self.client().get('/categories/1000/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['error'], 404)
        self.assertEqual(data['message'], 'resource was not found')
        self.assertFalse(data['success'])

    def test_generate_quiz_question_without_data(self):
        res = self.client().post('/quizzes', json={})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['error'], 422)
        self.assertEqual(data['message'], 'Unprocessable Entity')
        self.assertFalse(data['success'])

    def test_generate_quiz_question_with_wrong_data(self):
        res = self.client().post('/quizzes', json={"previous_questions":[], "quiz_category":1000})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['error'], 422)
        self.assertEqual(data['message'], 'Unprocessable Entity')
        self.assertFalse(data['success'])

    def test_generate_quiz_question_with_valid_data(self):
        res = self.client().post('/quizzes', json={"previous_questions":[], "quiz_category":{"type":"click", "id": 0}})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['question'])
        self.assertIsNotNone(data['question'])
    
    def test_generate_quiz_question_with_wrong_data(self):
        res = self.client().post('/category', json={})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['error'], 422)
        self.assertEqual(data['message'], 'Unprocessable Entity')
        self.assertFalse(data['success'])

    def test_generate_quiz_question_with_valid_data(self):
        res = self.client().post('/category', json={"cat_type":'new_cat'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()