from flask import Flask, render_template
app = Flask(__name__)

@app.route('/')
def placeholder():
    return render_template('placeholder.html')
    
app.run(host='0.0.0.0', port=8080)