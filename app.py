from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from os import getcwd
from flask import (
    Flask,
    request,
    jsonify,
    make_response
)


# Application settings:
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{getcwd()}/courses.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


# Database settings:
db = SQLAlchemy(app)


class Courses(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, default=datetime.utcnow)
    lessons = db.Column(db.Integer, default=0)

    def get_readable_course(course):
        return {
            'name': course.name,
            'start_date': course.start_date,
            'end_date': course.end_date,
            'lessons': course.lessons
        }

    def __repr__(self):
        return f'<course {self.id}>'


# Inner variables and API's:
db_fields_and_types = {
    'name': str,
    'start_date': datetime,
    'end_date': datetime,
    'lessons': int
}


def get_valid_request_data():
    try:
        request_data = request.get_json()
    except Exception:
        return {'error': 'Incorrect request data..'}
    else:
        return request_data


def get_valid_date(data):
    try:
        date = datetime.strptime(data, '%Y-%m-%d %H:%M:%S')
    except Exception:
        return False
    else:
        return date


def request_data_handler():
    if not request.is_json:
        return {'error': 'No json received..'}

    request_data = get_valid_request_data()

    if 'error' in request_data:
        return request_data

    fields = db_fields_and_types.keys()

    if request.method in ['GET', 'PATCH']:
        fields = request_data.keys()

    valid_data = dict()

    for field in fields:
        if field not in request_data:
            return {'error': f"Field '{field}' not found.."}

        current_data = request_data[field]
        is_date = get_valid_date(current_data)

        if is_date:
            current_data = is_date

        if (field in db_fields_and_types.keys() and
                not isinstance(current_data, db_fields_and_types.get(field))):
            return {'error': f"Incorrect type of '{field}' field.."}

        valid_data.update({field: current_data})
    return valid_data


# Routes:
# 0. Incorrect request address:
@app.errorhandler(404)
def address_not_found(_):
    return make_response(jsonify({'error': 'Non-existent address ..'}), 404)


# 1. Add a new course:
@app.route('/courses/add', methods=['POST'])
def add_course():
    process_data = request_data_handler()

    if 'error' in process_data:
        return make_response(jsonify(process_data), 400)

    new_course = Courses(
        name=process_data['name'],
        start_date=process_data['start_date'],
        end_date=process_data['end_date'],
        lessons=process_data['lessons']
    )
    try:
        db.session.add(new_course)
        db.session.commit()
    except Exception as expt:
        db.session.rollback()
        return make_response(jsonify({'error': str(expt)}), 400)
    else:
        return make_response(jsonify({'status': 'Course added!'}), 201)


# 2. Get all courses:
@app.route('/courses', methods=['GET'])
def get_all_courses():
    courses = [
        Courses.get_readable_course(course) for course in Courses.query.all()
    ]
    return make_response(jsonify(courses), 200)


# 3. Get course details by id:
@app.route('/courses/<int:id>', methods=['GET'])
def get_course_by_id(id):
    course = Courses.query.get(id)
    if course:
        course = Courses.get_readable_course(course)
        return make_response(jsonify(course), 200)
    return make_response(jsonify({'status': 'Course not found..'}), 200)


# 4. Get course datail by name and filter by date:
@app.route('/courses/<name>', methods=['GET'])
def get_courses_by_name_and_date(name):

    bottom_date = get_valid_date(
        request.args.get('bottom_date')
    )
    top_date = get_valid_date(
        request.args.get('top_date')
    )

    if not isinstance(bottom_date, datetime):
        bottom_date = datetime.today()

    if not isinstance(top_date, datetime):
        now = datetime.today()
        top_date = now.replace(year=now.year + 1)

    courses = [
        Courses.get_readable_course(course)
        for course in Courses.query.filter(
            (Courses.name == name) &
            (Courses.start_date >= bottom_date) &
            (Courses.start_date <= top_date)
        ).all()
    ]
    return make_response(jsonify(courses), 200)


# 5. Update course attributes:
@app.route('/courses/<int:id>', methods=['PATCH'])
def update_course(id):
    process_data = request_data_handler()

    if 'error' in process_data:
        return make_response(jsonify(process_data), 400)

    course = Courses.query.get(id)

    if course:
        course.name = process_data.get('name', course.name)
        course.start_date = process_data.get('start_date', course.start_date)
        course.end_date = process_data.get('end_date', course.end_date)
        course.lessons = process_data.get('lessons', course.lessons)

        try:
            db.session.commit()
        except Exception as expt:
            return make_response(jsonify({'error': str(expt)}), 404)
    return make_response('', 204)


# 6. Delete course by id:
@app.route('/courses/<int:id>', methods=['DELETE'])
def delete_course(id):
    Courses.query.filter_by(id=id).delete()
    try:
        db.session.commit()
    except Exception as expt:
        db.session.rollback()
        return make_response(jsonify({'error': str(expt)}), 404)
    else:
        return make_response('', 204)


if __name__ == '__main__':
    app.run(port=8001)
