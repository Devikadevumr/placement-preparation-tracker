from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])

def analyze():
    aptitude = int(request.form['aptitude'])
    coding = int(request.form['coding'])
    core = int(request.form['core'])

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

    return render_template(
        'result.html',
        aptitude_status=aptitude_status,
        coding_status=coding_status,
        core_status=core_status
    )


if __name__ == '__main__':
    app.run(debug=True)

