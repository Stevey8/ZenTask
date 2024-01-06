# to open the file/webpage: enter the following in the terminal
# python app.py

# create a database by typing the following in a python shell
# python 
# from app import app, db, Todo
# with app.app_context(): 
# db.drop_all() # only if want to clear the database
# db.create_all()

from flask import Flask, render_template, request, redirect
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
    completed = db.Column(db.Integer, default=0)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    date_due = db.Column(db.DateTime, nullable=True)
    importance = db.Column(db.String(50), nullable = False)

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
    '''get the 4 most important tasks. if less then four, return some quotes for now.'''
    sorted_tasks = sorted(tasks, key=lambda x: x.get_i_score(), reverse=True)
    if len(tasks)<4:
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
        if len(tasks)>0:
            top_four = get_first_four_tasks(tasks)
        else:
            top_four = [None,None,None,None]
        return render_template('task.html', tasks = tasks, top_four = top_four)
    

# template df 
@app.route('/df')
def show_df():
    tasks = Todo.query.order_by(Todo.date_created).all()
    return render_template('df.html', tasks = tasks)

    




# create a dataframe 

# df = pd.DataFrame({'Name': ['Alice', 'Bob', 'Charlie'], 'Age': [25, 30, 35]})
# html_table = df.to_html(index=False)

# @app.route('/df')
# def show_df():
#     html_table = df.to_html(index=False)
#     return render_template('df.html', html_table=html_table)




@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = Todo.query.get_or_404(id)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'There was a problem deleting that task'
    

@app.route('/update/<int:id>', methods=['GET','POST'])
def update(id):
    task = Todo.query.get_or_404(id)
    if request.method=='POST':
        task.content = request.form['content']

        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'There was a problem updating the task'
    
    else:
        return render_template('update.html', task=task)
    
    

if __name__ == '__main__':
    app.run(debug=True)
