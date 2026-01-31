from flask import Flask, render_template, request
import pandas as pd
from sklearn.linear_model import LogisticRegression

data = pd.read_csv("dataset.csv")

X = data[['aptitude', 'coding', 'core']]
y = data['placed']

model = LogisticRegression()
model.fit(X, y)

app = Flask(__name__)

@app.route('/')
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
def analyze():
    try:
        aptitude = int(request.form['aptitude'])
        coding = int(request.form['coding'])
        core = int(request.form['core'])

        if not (0 <= aptitude <= 100 and 0 <= coding <= 100 and 0 <= core <= 100):
            raise ValueError

    except:
        return render_template("error.html", message="Please enter valid scores between 0 and 100.")


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

    # ✅ DAY 6 logic MUST be inside analyze()
    scores = {
        "Aptitude": aptitude,
        "Coding": coding,
        "Core CS": core
    }

    weakest_subject = min(scores, key=scores.get)
    focus_message = f"Today focus on {weakest_subject} to improve placement readiness."

    scores = {
    "Aptitude": aptitude,
    "Coding": coding,
    "Core CS": core
    }

    weakest_subject = min(scores, key=scores.get)
    focus_message = f"Today focus on {weakest_subject}"

    # 🔥 ADD HERE
    average_score = round((aptitude + coding + core) / 3, 2)


    if average_score >= 70:
        readiness = "Placement Ready"
    elif average_score >= 50:
        readiness = "Almost Ready"
    else:
        readiness = "Needs Improvement"

        
    prediction = model.predict([[aptitude, coding, core]])[0]

    if prediction == 1:
        ml_result = "ML Prediction: Likely to Get Placed"
    else:
        ml_result = "ML Prediction: Needs Improvement"

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

    )

    


if __name__ == '__main__':
    app.run(debug=True)
