from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///diary.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    subtitle = db.Column(db.String, nullable=True)
    text = db.Column(db.Text, nullable=False)

@app.route('/')
def index():
    cards = Card.query.order_by(Card.id).all()
    return render_template('index.html', cards=cards)

@app.route('/card/<int:id>')
def card(id):
    card = Card.query.filter_by(id=id).first()
    return render_template('card.html', card=card)\
    
@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    card = Card.query.filter_by(id=id).first()
    db.session.delete(card)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/create')
def create():
    return render_template('create_card.html')

@app.route('/form_create', methods=['GET', 'POST'])
def form_create():
    if request.method == 'POST':
        title = request.form['title']
        subtitle = request.form['subtitle']
        text = request.form['text']

        card = Card(title=title, subtitle=subtitle, text=text)
        db.session.add(card)
        db.session.commit()

        return redirect(url_for('index'))
    return render_template('create_card.html')

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)