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


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(mail_address=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('ログイン成功しました！', 'success')
            return redirect(url_for('Home'))
        else:
            flash('ログインに失敗しました。再度ログインを実行してください', 'danger')
            print("test")
    return render_template('register_rewords/login.html') 

@app.route('/logout')
@login_required  # ログインしている場合のみアクセス可能
def logout():
    logout_user()  # ログアウト処理
    flash('You have been logged out!', 'info')  # フラッシュメッセージでログアウト完了を通知
    return redirect(url_for('Home'))  # ホームページにリダイレクト

@app.route('/add_points', methods=['POST'])
@login_required
def add_points():
    user_id = current_user.get_id()
    user = UserPoints.query.filter(UserPoints.user_id==user_id).first()  # 仮に1人のユーザーとして扱う場合
    user_history = UserPointsHistory.query.filter(
    UserPointsHistory.user_id == user_id,
    UserPointsHistory.created_at >= datetime.now().date(),
    UserPointsHistory.created_at < (datetime.now().date() + timedelta(days=1))
).first()
    if user_history is None:
        print('Aaa')
        user_history = UserPointsHistory(user_id=user_id, points=1)
    else:
        print(user_history.points)
        if check_date(user_history):
            user_history.points += 1
    user.points += 1  # 1ポイントを加算
    db.session.add(user)
    db.session.add(user_history)
    db.session.commit()
    return jsonify({'points': user.points})  # 最新のポイントを返す


@app.route('/get_points', methods=['GET'])
@login_required
def get_points():
    user_id = current_user.get_id()
    print(UserPointsHistory.query.first().points)
    user = UserPoints.query.filter(UserPoints.user_id==user_id).first() # 仮に1人のユーザーとして扱う場合 
    if user is None:
        user = UserPoints(points=0, user_id=user_id)
        db.session.add(user)
        db.session.commit()
    return jsonify({'points': user.points})

@app.route('/clear_cache')
def clear_cache():
    session.clear()  # セッションをクリア
    return redirect(url_for('Home'))  # トップページにリダイレクト

@app.route('/small_reword', methods=['GET']) #topページより送信されたsmall_rewordの情報を取得する
@login_required
def get_small_reword():
    user_id = current_user.get_id()
    rewords = []
    user_points = UserPoints.query.filter_by(user_id=user_id).first()
    small_reword = Reword.query.filter(Reword.reword_kind == 0, Reword.user_id == current_user.get_id()).all()
    print(user_points.points)
    for reword in small_reword:
        if int(user_points.points) >= int(reword.point):
            rewords.append(reword.name)
    if len(rewords):
        select_reword = rewords[random.randrange(0, len(rewords)-1)]
        small_reword = Reword.query.filter(Reword.reword_kind == 0, Reword.user_id == current_user.get_id(), Reword.name == select_reword).first()
        calc_points = user_points.points - small_reword.point
        user_points.points = calc_points
        db.session.commit()
        return jsonify({'reword': select_reword})
    return[]

@app.route('/big_reword', methods=['GET']) #topページより送信されたsmall_rewordの情報を取得する
@login_required
def get_big_reword():
    user_id = current_user.get_id()
    rewords = []
    user_points = UserPoints.query.filter_by(user_id=user_id).first()
    big_reword = Reword.query.filter(Reword.reword_kind == 1, Reword.user_id == current_user.get_id()).all()
    print(user_points.points)
    for reword in big_reword:
        if int(user_points.points) >= int(reword.point):
            rewords.append(reword.name)
    if len(rewords):
        select_reword = rewords[random.randrange(0, len(rewords)-1)]
        big_reword = Reword.query.filter(Reword.reword_kind == 1, Reword.user_id == current_user.get_id(), Reword.name == select_reword).first()
        calc_points = user_points.points - big_reword.point
        user_points.points = calc_points
        db.session.commit()
        return jsonify({'reword': select_reword})
    return[]



@app.route('/add', methods=['GET']) #addのページより送信された情報を取得して以下の関数を実行する
@login_required
def add_get():
    small_reword = Reword.query.filter(Reword.reword_kind == 0, Reword.user_id == current_user.get_id())
    big_reword = Reword.query.filter(Reword.reword_kind == 1, Reword.user_id == current_user.get_id())
    return render_template('register_rewords/index.html', small_reword=small_reword, big_reword=big_reword)


@app.route('/update', methods=['POST']) #Idのアップデートのリクエストをデータベースに送信する
@login_required
def update():
    id = request.form["id"]
    name = request.form["reword"]
    reword = Reword.query.filter_by(id=id).first()
    reword.name = name
    db.session.commit()
    return redirect("/add")


@app.route('/delete', methods=['POST']) #deleteしたIDの情報をデータベースの送信する
@login_required
def delete():
    id = request.form["id"]
    record_to_delete = Reword.query.filter_by(id=id).first() 
    db.session.delete(record_to_delete)
    db.session.commit()
    return redirect("/add")


@app.route('/create', methods=['POST']) #作成したrewordの情報をデータベースに送信する
@login_required
def add():
    reword_kind = False
    if request.form.get('reword_kind') is not None:
        reword_kind = True
        points = random.randrange(1, 2)
    else:
        reword_kind = False
        points =  random.randrange(3, 4)
    reword_text = request.form['reword']
    user_id = current_user.get_id()
    new_reword = Reword(name=reword_text, reword_kind=reword_kind, user_id=user_id, point=points)
    db.session.add(new_reword)
    print(user_id, points)
    db.session.commit()
    return redirect("/add")


@app.route('/stopwatch')
@login_required
def stopwatch():
    user_id = current_user.get_id()
    return render_template('register_rewords/stopwatch.html', user_id=user_id)


































































































