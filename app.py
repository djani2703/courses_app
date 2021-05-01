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


def get_required_fields(data):
    if request.method in ['PATCH', 'GET']:
        return [
            field for field in data.keys()
        ]
    elif request.method in ['POST', 'PUT']:
        return db_fields_and_types.keys()


def request_data_handler():
    if not request.is_json:
        return {'error': 'No json received..'}

    try:
        data = request.get_json()
    except Exception:
        return {'error': 'Incorrect request data..'}

    required_fields = get_required_fields(data)
    valid_data = dict()

    for field in required_fields:
        if field not in data:
            return {'error': f"Field '{field}' not found.."}

        if db_fields_and_types.get(field) == datetime:
            try:
                valid_data.update({
                    field: datetime.strptime(data[field], '%Y-%m-%d %H:%M:%S')
                })
            except Exception:
                return {'error': f"Incorrect type of '{field}' field.."}
        else:
            if (field in db_fields_and_types.keys() and not
                isinstance(data.get(field), db_fields_and_types.get(field))):
                return {'error': f"Incorrect type of '{field}' field.."}
            valid_data.update({field: data[field]})
    return valid_data


# Routes:
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
        return make_response(jsonify({'status': 'Course added!'}), 200)


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
    return make_response(jsonify({'status': "Can't show the course.."}), 200)


# 4. Get course datail by name and filter by date:
@app.route('/courses/<name>', methods=['GET'])
def get_courses_by_name_and_date(name):
    process_data = request_data_handler()

    if 'error' in process_data:
        return make_response(jsonify(process_data), 400)

    now = datetime.today()
    bottom_date = process_data.get('bottom_date', now)
    top_date = process_data.get('top_date', now.replace(year=now.year + 1))

    try:
        if isinstance(bottom_date, str):
            bottom_date = datetime.strptime(bottom_date, '%Y-%m-%d %H:%M:%S')

        if isinstance(top_date, str):
            top_date = datetime.strptime(top_date, '%Y-%m-%d %H:%M:%S')
    except Exception as expt:
        return make_response(jsonify({'error': str(expt)}), 400)

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
def change_course(id):
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
