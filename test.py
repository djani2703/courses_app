import unittest
import requests
from random import randint


class APITest(unittest.TestCase):
    COURSES_URL = 'http://127.0.0.1:8001/courses'
    CORRECT_DATA = {
        'name': 'Data Science',
        'start_date': '2021-06-20 18:00:00',
        'end_date': '2022-07-21 21:00:00',
        'lessons': 18
    }

    NO_FIELD_DATA = {
        'name': 'Advanced Python',
        'start_date': '2021-10-20 18:00:00',
        'end_date': '2022-11-21 21:00:00'
    }

    WRONG_FIELD_DATA = {
        'name': 'Big Data',
        'start_date': '2021-06-20 18:00:00',
        'end_date': '2022-07-21',
        'lessons': 18
    }

    def check_correct_response(self, *data):
        (response, code, field, msg, data_type, cases) = data

        if 1 in cases:
            self.assertEqual(response.status_code, code)

        if 2 in cases:
            self.assertTrue(field in response.json())

        if 3 in cases:
            self.assertEqual(response.json().get(field), msg)

        if 4 in cases:
            self.assertIsInstance(response.json(), data_type)

    def test_add_new_course(self):
        ADD_URL = APITest.COURSES_URL + '/add'

        # Correct data:
        response = requests.post(ADD_URL, json=APITest.CORRECT_DATA)
        self.check_correct_response(
            response, 201, 'status', 'Course added!', None, [1, 2, 3]
        )

        # No JSON received:
        response = requests.post(ADD_URL, APITest.CORRECT_DATA)
        self.check_correct_response(
            response, 400, 'error', 'No json received..', None, [1, 2, 3]
        )

        # Missing field in data:
        response = requests.post(ADD_URL, json=APITest.NO_FIELD_DATA)
        self.check_correct_response(
            response, 400, 'error', "Field 'lessons' not found..",
            None, [1, 2, 3]
        )

        # Incorrect course field data:
        response = requests.post(ADD_URL, json=APITest.WRONG_FIELD_DATA)
        self.check_correct_response(
            response, 400, 'error', "Incorrect type of 'end_date' field..",
            None, [1, 2, 3]
        )

    def test_get_all_courses(self):
        response = requests.get(APITest.COURSES_URL)
        self.check_correct_response(
            response, 200, None, None, list, [1, 4]
        )

    def test_get_course_by_id(self):
        course_id = 1
        response = requests.get(APITest.COURSES_URL + f'/{course_id}')
        self.check_correct_response(
            response, 200, 'name', None, dict, [1, 2, 4]
        )

        course_id = randint(1000, 2000)
        response = requests.get(APITest.COURSES_URL + f'/{course_id}')
        self.check_correct_response(
            response, 200, 'status', 'Course not found..', None, [1, 2, 3]
        )

    def test_get_courses_by_name_and_date(self):
        for course_name in ['Data Science', 'Incorrect course name']:

            # Correct and incorrect name of course:
            URL1 = APITest.COURSES_URL + f'/{course_name}'
            response = requests.get(URL1)

            self.check_correct_response(
                response, 200, None, None, list, [1, 4]
            )

            # Correct and incorrect data for date filter:
            for bottom_date in [22, '2021-06-20 18:00:00']:
                URL2 = URL1 + f'?bottom_date={bottom_date}'
                response = requests.get(URL2)
                self.check_correct_response(
                    response, 200, None, None, list, [1, 4]
                )
                for top_date in ['2022-11-21 21:00:00', 'some string']:
                    URL3 = URL2 + f'&top_date={top_date}'
                    response = requests.get(URL3)
                    self.check_correct_response(
                        response, 200, None, None, list, [1, 4]
                    )

    def test_change_course(self):
        course_id = randint(1, 10)
        UPDATE_URL = APITest.COURSES_URL + f'/{course_id}'

        # Correct request data:
        response = requests.patch(UPDATE_URL, json=APITest.NO_FIELD_DATA)
        self.check_correct_response(
            response, 204, None, None, None, [1]
        )

        # No JSON received:
        response = requests.patch(UPDATE_URL, APITest.CORRECT_DATA)
        self.check_correct_response(
            response, 400, 'error', 'No json received..', None, [1, 2, 3]
        )

        # Incorrect course field data:
        response = requests.patch(UPDATE_URL, json=APITest.WRONG_FIELD_DATA)
        self.check_correct_response(
            response, 400, 'error', "Incorrect type of 'end_date' field..",
            None, [1, 2, 3]
        )

    def test_remove_course(self):
        course_id = 1
        response = requests.delete(APITest.COURSES_URL + f'/{course_id}')
        self.check_correct_response(
            response, 204, None, None, None, [1]
        )


if __name__ == '__main__':
    unittest.main()
