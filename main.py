from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///flask.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "your-secret-key-here" 
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Notes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    text = db.Column(db.Text, nullable=False)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)

@app.route("/")
def index():
    all_notes = Notes.query.all()
    return render_template("index.html", notes=all_notes)

@app.route("/add", methods=["POST"])
def add_note():

    title = request.form["title"]
    text = request.form["text"]
    
    new_note = Notes(title=title, text=text)
    db.session.add(new_note)
    db.session.commit()
    
    return redirect(url_for("index"))

@app.route("/notes")
def show_notes():
    all_notes = Notes.query.order_by(Notes.id.desc()).all()
    return render_template("notes.html", notes=all_notes)

@app.route("/home")
def home():
    return render_template("home.html")

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash("Пользователь с таким именем или email уже существует", "error")
            return render_template("register.html")
        
        hashed_password = generate_password_hash(password)
        
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        
        flash("Регистрация успешна! Теперь вы можете войти.", "success")
        return redirect(url_for("login"))
    
    return render_template("register.html")
        

def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash(f"Добро пожаловать, {username}!", "success")
            return redirect(url_for("index"))
        else:
            flash("Неверное имя пользователя или пароль", "error")
    
    return render_template("login.html")

@app.route("/delete/<int:note_id>")
def delete_note(note_id):
    note = Notes.query.get_or_404(note_id)
    db.session.delete(note)
    db.session.commit()
    return redirect(url_for("show_notes"))

if __name__ == "__main__":
    with app.app_context():
        db.create_all() 
    app.run(debug=True)
