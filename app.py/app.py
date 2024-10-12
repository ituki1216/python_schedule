from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///schedule.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# データベースモデル
class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(10), nullable=False)
    time = db.Column(db.String(5), nullable=False)
    description = db.Column(db.Text, nullable=True)

# スケジュール一覧ページ
@app.route('/')
def index():
    schedules = Schedule.query.all()
    return render_template('index.html', schedules=schedules)

# スケジュール追加
@app.route('/add', methods=['POST'])
def add_schedule():
    title = request.form['title']
    date = request.form['date']
    time = request.form['time']
    description = request.form['description']
    new_schedule = Schedule(title=title, date=date, time=time, description=description)
    db.session.add(new_schedule)
    db.session.commit()
    return redirect(url_for('index'))

# スケジュール削除
@app.route('/delete/<int:id>')
def delete_schedule(id):
    schedule = Schedule.query.get(id)
    db.session.delete(schedule)
    db.session.commit()
    return redirect(url_for('index'))

# スケジュール編集
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_schedule(id):
    schedule = Schedule.query.get(id)
    if request.method == 'POST':
        schedule.title = request.form['title']
        schedule.date = request.form['date']
        schedule.time = request.form['time']
        schedule.description = request.form['description']
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('edit.html', schedule=schedule)

if __name__ == '__main__':
    app.run(debug=True)
