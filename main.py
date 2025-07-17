#Импорт
from flask import Flask, render_template, request, redirect, session, url_for
#Подключение библиотеки баз данных
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
#Задаем секретный ключ для работы session
app.secret_key = 'my_top_secret_123'
#Подключение SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///diary.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#Создание db
db = SQLAlchemy(app)

class Card(db.Model):
    #Создание полей
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    subtitle = db.Column(db.String(300), nullable=False)
    text = db.Column(db.Text, nullable=False)
    user_email = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<Card {self.id}>'

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String(70), nullable=False)

@app.route('/', methods=['GET','POST'])
def login():
    error = ''
    if request.method == 'POST':
        form_login = request.form['email']
        form_password = request.form['password']
            
        user = User.query.filter_by(email=form_login).first()
        if not user:
            error = "Неверный логин или пароль."
        elif user.password != form_password:
            error = "Неверный логин или пароль."
        else:
            session['user_email'] = user.email
            return redirect(url_for('index'))
    
    return render_template('login.html', error=error)

@app.route('/reg', methods=['GET','POST'])
def reg():
    error = ''
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        if User.query.filter_by(email=email).first():
            error = "Такой пользователь уже существует"
        elif len(password) < 8:
            error = "Пароль должен иметь 8 или более символов"
        else:
            user = User(email=email, password=password)
            db.session.add(user)
            db.session.commit()
            session['user_email'] = email
            return redirect(url_for('index'))
    
    return render_template('registration.html', error=error)

@app.route('/index')
def index():
    if 'user_email' not in session:
        return redirect(url_for('login'))
    
    cards = Card.query.filter_by(user_email=session['user_email']).order_by(Card.id).all()
    return render_template('index.html', cards=cards)

@app.route('/card/<int:id>')
def card(id):
    if 'user_email' not in session:
        return redirect(url_for('login'))
    
    card = Card.query.get_or_404(id)
    if card.user_email != session['user_email']:
        return redirect(url_for('index'))
    
    return render_template('card.html', card=card)

@app.route('/create')
def create():
    if 'user_email' not in session:
        return redirect(url_for('login'))
    return render_template('create_card.html')

@app.route('/form_create', methods=['GET','POST'])
def form_create():
    if 'user_email' not in session:
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        title = request.form['title']
        subtitle = request.form['subtitle']
        text = request.form['text']

        card = Card(
            title=title, 
            subtitle=subtitle, 
            text=text, 
            user_email=session['user_email']
        )
        db.session.add(card)
        db.session.commit()
        return redirect(url_for('index'))
    
    return render_template('create_card.html')

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)