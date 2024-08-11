from flask import Flask, render_template_string, request, redirect, url_for, session
import json
import os

app = Flask(__name__)
app.secret_key = '8113261ameerkhan012'  # Change this to a random string for security

# File paths for JSON data
USERS_FILE = 'users.json'
TASKS_FILE = 'tasks.json'

def load_data(filename):
    if not os.path.exists(filename):
        with open(filename, 'w') as file:
            json.dump({}, file)
    with open(filename, 'r') as file:
        return json.load(file)

def save_data(filename, data):
    with open(filename, 'w') as file:
        json.dump(data, file)

# HTML and CSS templates
LOGIN_HTML = '''
<!doctype html>
<html>
<head>
    <title>Login</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #fafafa;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }
        .container {
            max-width: 400px;
            width: 100%;
            background: #fff;
            padding: 20px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
            border-radius: 8px;
        }
        h2 {
            text-align: center;
            margin-bottom: 20px;
            color: #333;
        }
        input {
            width: 100%;
            padding: 10px;
            margin: 10px 0;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        button {
            width: 100%;
            padding: 10px;
            border: none;
            background: #0095f6;
            color: #fff;
            border-radius: 4px;
            cursor: pointer;
        }
        button:hover {
            background: #007bb5;
        }
        .links {
            text-align: center;
            margin-top: 10px;
        }
        .links a {
            color: #0095f6;
            text-decoration: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>Login</h2>
        <form method="post">
            <input type="text" name="username" placeholder="Username" required>
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit">Login</button>
        </form>
        <div class="links">
            <p>Don't have an account? <a href="{{ url_for('signup') }}">Sign up</a></p>
        </div>
    </div>
</body>
</html>
'''

SIGNUP_HTML = '''
<!doctype html>
<html>
<head>
    <title>Signup</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #fafafa;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }
        .container {
            max-width: 400px;
            width: 100%;
            background: #fff;
            padding: 20px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
            border-radius: 8px;
        }
        h2 {
            text-align: center;
            margin-bottom: 20px;
            color: #333;
        }
        input {
            width: 100%;
            padding: 10px;
            margin: 10px 0;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        button {
            width: 100%;
            padding: 10px;
            border: none;
            background: #0095f6;
            color: #fff;
            border-radius: 4px;
            cursor: pointer;
        }
        button:hover {
            background: #007bb5;
        }
        .links {
            text-align: center;
            margin-top: 10px;
        }
        .links a {
            color: #0095f6;
            text-decoration: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>Signup</h2>
        <form method="post">
            <input type="text" name="username" placeholder="Username" required>
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit">Signup</button>
        </form>
        <div class="links">
            <p>Already have an account? <a href="{{ url_for('login') }}">Login</a></p>
        </div>
    </div>
</body>
</html>
'''

INDEX_HTML = '''
<!doctype html>
<html>
<head>
    <title>To-Do List</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #fafafa;
            display: flex;
            flex-direction: column;
            align-items: center;
            height: 100vh;
            margin: 0;
        }
        .container {
            max-width: 600px;
            width: 100%;
            background: #fff;
            padding: 20px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
            border-radius: 8px;
            margin-top: 20px;
        }
        h2 {
            text-align: center;
            margin-bottom: 20px;
            color: #333;
        }
        input[type="text"] {
            width: calc(100% - 22px);
            padding: 10px;
            margin: 10px 0;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        button {
            width: 100%;
            padding: 10px;
            border: none;
            background: #0095f6;
            color: #fff;
            border-radius: 4px;
            cursor: pointer;
        }
        button:hover {
            background: #007bb5;
        }
        ul {
            list-style: none;
            padding: 0;
        }
        li {
            display: flex;
            align-items: center;
            padding: 10px;
            border-bottom: 1px solid #ddd;
        }
        input[type="checkbox"] {
            margin-right: 10px;
        }
        .delete {
            margin-left: auto;
            color: #f00;
            cursor: pointer;
        }
        .delete:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>To-Do List</h2>
        <form method="post" action="{{ url_for('add_task') }}">
            <input type="text" name="task" placeholder="New task" required>
            <button type="submit">Add Task</button>
        </form>
        <ul>
            {% for task in tasks %}
                <li>
                    <input type="checkbox" {% if task.completed %}checked{% endif %} onclick="location.href='{{ url_for('toggle_task', task_id=loop.index0) }}'">
                    {{ task.task }}
                    <a href="{{ url_for('delete_task', task_id=loop.index0) }}" class="delete">Delete</a>
                </li>
            {% endfor %}
        </ul>
        <a href="{{ url_for('logout') }}">Logout</a>
    </div>
</body>
</html>
'''

@app.route('/')
def index():
    if 'username' in session:
        tasks = load_data(TASKS_FILE).get(session['username'], [])
        return render_template_string(INDEX_HTML, tasks=tasks)
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users = load_data(USERS_FILE)
        if username in users and users[username] == password:
            session['username'] = username
            return redirect(url_for('index'))
        return 'Invalid username or password'
    return render_template_string(LOGIN_HTML)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users = load_data(USERS_FILE)
        if username in users:
            return 'Username already exists'
        users[username] = password
        save_data(USERS_FILE, users)
        session['username'] = username
        return redirect(url_for('index'))
    return render_template_string(SIGNUP_HTML)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/add_task', methods=['POST'])
def add_task():
    if 'username' in session:
        task = request.form['task']
        tasks = load_data(TASKS_FILE)
        user_tasks = tasks.get(session['username'], [])
        user_tasks.append({'task': task, 'completed': False})
        tasks[session['username']] = user_tasks
        save_data(TASKS_FILE, tasks)
    return redirect(url_for('index'))

@app.route('/toggle_task/<int:task_id>')
def toggle_task(task_id):
    if 'username' in session:
        tasks = load_data(TASKS_FILE)
        user_tasks = tasks.get(session['username'], [])
        if 0 <= task_id < len(user_tasks):
            user_tasks[task_id]['completed'] = not user_tasks[task_id]['completed']
            save_data(TASKS_FILE, tasks)
    return redirect(url_for('index'))

@app.route('/delete_task/<int:task_id>')
def delete_task(task_id):
    if 'username' in session:
        tasks = load_data(TASKS_FILE)
        user_tasks = tasks.get(session['username'], [])
        if 0 <= task_id < len(user_tasks):
            del user_tasks[task_id]
            tasks[session['username']] = user_tasks
            save_data(TASKS_FILE, tasks)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=False)
