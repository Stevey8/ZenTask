# to open the file/webpage: enter the following in the terminal
# python app.py

# create a database by typing the following in a python shell
# python 
# from app import app, db, Todo
# with app.app_context(): 
# db.drop_all() # only if want to clear the database
# db.create_all()

from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pandas as pd 

app = Flask(__name__, static_url_path='/static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False) # nullable = True to make it 'blank'able
    label = db.Column(db.String(50), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    date_due = db.Column(db.DateTime, nullable=True)
    importance = db.Column(db.String(50), nullable = False)
    completed = db.Column(db.Integer, default=0)


    def get_i_score(self):
        if self.importance=='default':
            return 0
        elif self.importance=='kinda':
            return 3.5 
        elif self.importance=='urgent':
            return 6.5
        elif self.importance=='date_dependent':
            time_left = self.date_due-datetime.now()
            days_left = time_left.days
            score = max(0,7-days_left) 
            return score
        else:
            raise ValueError("there are some errors")
 
    def __repr__(self):
        return '<Task %r>' % self.id
    
    
def get_first_four_tasks(tasks):
    '''get the 4 most important tasks for home page. if less then four, return some quotes for now.'''

    todo_tasks = [t for t in tasks if t.completed==0]
    sorted_tasks = sorted(todo_tasks, key=lambda x: x.get_i_score(), reverse=True)

    if len(todo_tasks)<4:
        sorted_tasks_copy = sorted_tasks.copy()
        sorted_tasks_copy.extend([None,None,None,None])
        return sorted_tasks_copy[:4]
    else:
        return sorted_tasks[:4]




@app.route('/', methods=['POST','GET'])
def index():
    if request.method == 'POST':
        task_content = request.form['content']
        task_label = request.form['label']
        if request.form['date_due'] == '':
            task_date_due = None
        else:
            task_date_due = datetime.strptime(request.form['date_due'], '%Y-%m-%d').replace(hour=23, minute=59)
        task_importance = request.form['importance']

        new_task = Todo(content=task_content, label=task_label, date_due=task_date_due, importance = task_importance)

        try: 
            db.session.add(new_task)
            db.session.commit()
            return redirect('/')
        except Exception as e:
            print(e)
            return 'there was an issue adding your task:   ' + str(e)
        
    else:
        tasks = Todo.query.order_by(Todo.date_created).all()
        top_four = get_first_four_tasks(tasks)
        return render_template('task.html', top_four = top_four)
    

@app.route('/task')
def task():
    tasks = Todo.query.order_by(Todo.date_created).all()
    top_four = get_first_four_tasks(tasks)
    return render_template('task.html', top_four = top_four)

@app.route('/df')
def show_df():
    tasks = Todo.query.order_by(Todo.date_created).all().copy()
    todo_tasks = [t for t in tasks if t.completed==0]
    # for t in todo_tasks:
    #     if t.date_due==None:
    #         t.date_due = datetime(1970, 1, 1)
    sorted_tasks = sorted(
        todo_tasks,
        key=lambda x: (x.get_i_score()*(-1), x.date_due if x.date_due is not None else datetime.max),
    )
    return render_template('df.html', tasks = sorted_tasks)

@app.route('/done')
def done():
    tasks = Todo.query.order_by(Todo.date_created).all()
    done_tasks = [t for t in tasks if t.completed]
    return render_template('done.html', tasks = done_tasks)


# when clicking "Done!"
@app.route('/complete/<int:id>')
def complete(id):
    task = Todo.query.get_or_404(id)
    try:
        task.completed=True
        db.session.commit()
        return redirect('/df')
    except:
        return 'There was a problem completing the task'
    

@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = Todo.query.get_or_404(id)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/df')
    except:
        return 'There was a problem deleting that task'
    

@app.route('/update/<int:id>', methods=['GET','POST'])
def update(id):
    task = Todo.query.get_or_404(id)
    if request.method=='POST':
        task.content = request.form['content']

        try:
            db.session.commit()
            return redirect('/df')
        except:
            return 'There was a problem updating the task'
    
    else:
        return render_template('update.html', task=task)
    
    

if __name__ == '__main__':
    app.run(debug=True)


# create a dataframe 

# df = pd.DataFrame({'Name': ['Alice', 'Bob', 'Charlie'], 'Age': [25, 30, 35]})
# html_table = df.to_html(index=False)

# @app.route('/df')
# def show_df():
#     html_table = df.to_html(index=False)
#     return render_template('df.html', html_table=html_table)


# trying 