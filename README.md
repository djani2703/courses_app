<h3>Step-by-step instructions for deploying, using, and testing the courses API (terminal commands, UNIX-like systems)</h3>
<p>1. First of all, you need to clone the project: git clone https://github.com/djani2703/courses_app.git</p>
<p>2. Go to courses_app directory: cd courses_app</p>
<p>3. Create a virtual environment: virtualenv -p python3 venv</p>
<p>4. Activate your virtual environment: source venv/bin/activate</p>
<p>5. Install all required libraries: pip3 install -r requirements.txt</p>
<p>6. Run Python3 interpreter in terminal to create database: python3</p>
<p>7. Input the following commands:</p> 
    <ul>
        <li><p>from app import db</p></li>
        <li><p>db.create_all()</p></li>
    </ul>
<p>8. Exit the terminal: exit() or Ctrl+d</p>
<p>9. Start application: python3 app.py</p>
<p>10. You can run tests for the application: python3 test.py</p>
<p>11. Work with the application with the following commands (curl):</p>
<br/>
<p>1. Add a new course:<br/>
<b>curl -X POST '127.0.0.1:8001/courses/add' -H 'Content-Type: application/json' -d '{
        "name": "Data Science",
        "start_date": "2021-11-20 18:00:00",
        "end_date": "2022-01-21 21:00:00",
        "lessons": 8
}'</b></p>
<p>2.Get all courses:<br/><b>curl -X GET '127.0.0.1:8001/courses' -H 'Content-Type: application/json'</b></p>
<p>3. Get courses by ID:<br/><b>curl -X GET '127.0.0.1:8001/courses/1' -H 'Content-Type: application/json'</b></p>
<p>4. Get courses by name with filter data:<br/><b>curl -X GET '127.0.0.1:8001/courses/Data%20Science?bottom_date=2021-06-20%2018:00:00&top_date=2021-10-20%2018:00:00'</b></p>
<p>5. Update fields of course:<br/><b>curl -X PATCH '127.0.0.1:8001/courses/1' -H 'Content-Type: application/json' -d '{
    "name": "Python",
    "start_date": "2021-05-24 18:00:00",
    "end_date": "2021-07-24 20:00:00",
    "lessons": 21
}'</b></p>
<p>6. Delete course by ID:<br/><b>curl -X DELETE '127.0.0.1:8001/courses/1'</b></p>
<p>*All these operations can be performed in Postman: copy the entire curl into the Postman import window and run it in the program</p>
<p>**I apologize that I didn't design README.md file more beautifully:)</p>