import sys
import os

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template, request, redirect, url_for
import maestro_groq

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        objective = request.form.get('objective')
        if objective:
            indexFileName = maestro_groq.run_maestro(objective)
            return render_template(indexFileName)
    return render_template('index.html')

@app.route('/results')
def results():
    return "This page will display the results."

if __name__ == '__main__':
    app.run(debug=True)
