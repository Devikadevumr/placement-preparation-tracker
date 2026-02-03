from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd
from sklearn.linear_model import LogisticRegression
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    login_required,
    logout_user
)

# ================= ML MODEL =================
data = pd.read_csv("dataset.csv")

X = data[['aptitude', 'coding', 'core']]
y = data['placed']

model = LogisticRegression()
model.fit(X, y)

# ================= APP SETUP =================
app = Flask(__name__)
app.config['SECRET_KEY'] = 'devu_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# ================= USER MODEL =================
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ================= AUTH ROUTES =================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username, password=password).first()

        if user:
            login_user(user)
            return redirect(url_for('home'))

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if User.query.filter_by(username=username).first():
            return render_template('register.html', error="Username already exists")

        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# ================= MAIN ROUTES =================
@app.route('/')
@login_required
def home():
    return render_template('index.html')


def get_suggestion(status, subject):
    if status == "Weak":
        if subject == "aptitude":
            return "Practice quantitative aptitude and logical reasoning daily."
        elif subject == "coding":
            return "Focus on DSA problems and coding practice."
        elif subject == "core":
            return "Revise DBMS, OS, and Computer Networks."
    elif status == "Average":
        return "Keep practicing to strengthen this area."
    else:
        return "Excellent performance. Maintain consistency."


@app.route('/analyze', methods=['POST'])
@login_required
def analyze():
    try:
        aptitude = int(request.form['aptitude'])
        coding = int(request.form['coding'])
        core = int(request.form['core'])

        if not (0 <= aptitude <= 100 and 0 <= coding <= 100 and 0 <= core <= 100):
            raise ValueError

    except:
        
        return render_template("error.html", message="Please enter valid scores between 0 and 100.")

    # ---- Analysis ----
    def analyze_score(score):
        if score < 50:
            return "Weak"
        elif score <= 75:
            return "Average"
        else:
            return "Strong"

    aptitude_status = analyze_score(aptitude)
    coding_status = analyze_score(coding)
    core_status = analyze_score(core)

    aptitude_suggestion = get_suggestion(aptitude_status, "aptitude")
    coding_suggestion = get_suggestion(coding_status, "coding")
    core_suggestion = get_suggestion(core_status, "core")

    # ---- Daily Focus ----
    scores = {
        "Aptitude": aptitude,
        "Coding": coding,
        "Core CS": core
    }

    weakest_subject = min(scores, key=scores.get)
    focus_message = f"Today focus on {weakest_subject}"

    # ---- Readiness ----
    average_score = round((aptitude + coding + core) / 3, 2)

    if average_score >= 70:
        readiness = "Placement Ready"
    elif average_score >= 50:
        readiness = "Almost Ready"
    else:
        readiness = "Needs Improvement"

    # ---- ML Prediction ----
    prediction = model.predict([[aptitude, coding, core]])[0]

    if prediction == 1:
        ml_result = "ML Prediction: Likely to Get Placed"
    else:
        ml_result = "ML Prediction: Needs Improvement"
    # store scores for chart page
    session['aptitude'] = aptitude
    session['coding'] = coding
    session['core'] = core

    return render_template(
        'result.html',
        aptitude_status=aptitude_status,
        coding_status=coding_status,
        core_status=core_status,
        aptitude_suggestion=aptitude_suggestion,
        coding_suggestion=coding_suggestion,
        core_suggestion=core_suggestion,
        focus_message=focus_message,
        readiness=readiness,
        average_score=average_score,
        ml_result=ml_result,
        aptitude=aptitude,
        coding=coding,
        core=core
    )
@app.route('/chart')
@login_required
def chart():
    return render_template('chart.html')

# ================= RUN =================
if __name__ == '__main__':
    app.run(debug=True)
