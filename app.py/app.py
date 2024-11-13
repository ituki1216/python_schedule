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

































































































・先日、就業先に退職の意をお伝えしたところ、こちらの意をくみとっていただき今月末の退職でも大丈夫と言っていただいておりまして、
現在1/6日入社となっておりますが、12月中の入社は再度ご検討いただけたりしますでしょうか？

・フルリモートでの勤務ということで定期的なコミュニケーションをとる機会があるか、またある場合頻度を教えてください。

・入社までにこれくらいは最低限出来るようになっていてほしい、または意味くらいは理解しておいてほしいなどの技術があればいくつでも大丈夫ですので、
教えていただきたいです

・多田さん、鈴木さん以外にバックエンドの方はどれくらい在籍しているのか、フロント、バックエンド含めチームの規模感を教えていただきたいです。

・開発において、GitやGitHubは使用されていますか？もし使用している場合、主にどのような形で活用されているか、チームのワークフローについて教えていただけますか？

・前回、お伝えしていただいたかもしれませんが、忘れてしまった為、業務上でのコミュニケーションツールは主に何を使用して行っていますか？

・入社日当日の流れや、一か月、一年間の想定している私の業務内容、役割はどのような事を想定していますでしょうか？

・皆さんの休憩時間についてお伺いしたいのですが、いつも決まった時間に休憩時間を取得されているのか、休憩したい任意の時間からできるのか教えてください。

・何かの機会で、東京の本社の方に行くことは今後の予定でありますでしょうか？

・フルリモート勤務を行う上で鈴木さんや多田さんが気を付けていることはなんですか？

・面接の際に希望年収を聞かれた時に、250万円とお答えしたのですが、それ以上の条件を提示していただきありがとうございます。
もし将来的に年収を350万円にアップさせたいと思う場合、私がその年収に到達するまでに、どのようなスキルや経験を積む必要があるか、
具体的な目安があれば教えていただけますか？また評価制度についても教えてください。




株式会社ケー・アンド・エル
金子 様

お世話になっております。山中です。
本日のオファー面談で色々質問の機会もあるのかなとは思うのですが、先に一点優先的にご質問したいことがあります。

先日、内定のお知らせを頂き親会社、並びに就業先に転職の意をお伝えしましたところ、こちらの意をくみ取っていただき、今月末の退縮でも大丈夫とお返事を頂きました。
現在、条件通知書の方には1/6日入社日と記載されておりますが、12月中に入社が可能かどうか再度、ご検討していただく事は可能でしょうか？

お忙しいところ、恐れ入りますが何卒よろしくお願い申し上げます。

ーーーーーーーーーーーーーーーーーーーーー
山中 一樹
TEL：090-6248-3786
MAIL ： yamanakasan@icloud.com
