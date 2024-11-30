from flask import Flask, request, render_template, redirect, url_for, flash,jsonify

import sqlite3

import os

currentdirectory = os.path.dirname(os.path.abspath(__file__))
print("Current directory:", currentdirectory)


# Define the directory and create the Flask app
currentdirectory = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__)

tasks = {}

# Database connection function
def get_db_connection():
    conn = sqlite3.connect(os.path.join(currentdirectory, 'tasks.db'))
    conn.row_factory = sqlite3.Row  # To access columns as dictionary
    return conn

# Route to render the home page
@app.route("/")
def main():
    # Get the status filter from the query parameters
    status_filter = request.args.get('status')  # `None` means no filter applied
    
    conn = get_db_connection()
    
    if status_filter:
        # Fetch tasks filtered by the selected status
        tasks = conn.execute('SELECT * FROM tasks WHERE status = ?', (status_filter,)).fetchall()
    else:
        # Fetch all tasks if no filter is applied
        tasks = conn.execute('SELECT * FROM tasks').fetchall()
    
    conn.close()
    
    # Render the home page with the tasks and current filter
    return render_template("home.html", tasks=tasks, status_filter=status_filter)

@app.route('/delete-task/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    conn = get_db_connection()
    
    # Execute the delete query
    conn.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()
    
    return redirect(url_for('main'))

@app.route('/toggle-status/<int:task_id>', methods=['POST'])
def toggle_status(task_id):
    # Debugging: Print the form data to check the received fields
    print("Form data received:", request.form)

    # Extract the status from the form data
    new_status = request.form.get('status')
    if not new_status:
        return jsonify({"error": "Status not provided"}), 400

    # Connect to the database and update status
    conn = get_db_connection()
    conn.execute(
        'UPDATE tasks SET status = ? WHERE id = ?',
        (new_status, task_id)
    )
    conn.commit()
    conn.close()

    return redirect(url_for('main'))




@app.route('/add-task', methods=['GET', 'POST'])
def add_task():
    if request.method == 'POST':
        # Retrieve data from the form
        title = request.form['title']
        description = request.form['description']
        due_date = request.form['due_date']
        status = request.form['status']

        # Insert the new task into the database
        conn = get_db_connection()
        conn.execute(
            'INSERT INTO tasks (title, description, due_date, status) VALUES (?, ?, ?, ?)',
            (title, description, due_date, status)
        )
        conn.commit()  # Commit the transaction
        conn.close()

        return redirect(url_for('main'))

    return render_template('add-task.html')


@app.route('/edit-task/<int:task_id>')
def task_form(task_id):
    # Fetch task details from the database based on the task_id
    conn = get_db_connection()
    task = conn.execute('SELECT * FROM tasks WHERE id = ?', (task_id,)).fetchone()
    conn.close()

    if task is None:
        # If task not found, return a 404 error
        return "Task not found", 404

    # Pass the task details to the template
    return render_template('edit-task.html', task=task)

@app.route('/update-task/<int:task_id>', methods=['POST'])
def update_task(task_id):
    # Get form data
    title = request.form['title']
    description = request.form['description']
    due_date = request.form['due_date']
    status = request.form['status']

    conn = get_db_connection()
    conn.execute(
        'UPDATE tasks SET title = ?, description = ?, due_date = ?, status = ? WHERE id = ?',
        (title, description, due_date, status, task_id)
    )
    conn.commit()
    conn.close()

    return redirect(url_for('main'))

# Route to view all tasks in JSON format (API route)
@app.route("/tasks")
def view_tasks():
    conn = get_db_connection()
    tasks = conn.execute('SELECT * FROM tasks').fetchall()
    conn.close()
    # Return tasks as JSON
    return jsonify([dict(task) for task in tasks])

if __name__ == "__main__":
    app.run(debug=True)
