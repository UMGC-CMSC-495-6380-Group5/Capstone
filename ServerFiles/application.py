from flask import Flask, render_template
from testform import TestForm

app = Flask(__name__)

app.config['SECRET_KEY'] ='12345'
  
@app.route('/placeholder')
def placeholder():
    my_variable = "This is a test string that will be passed to the HTML template"
    my_list = ["This", "is", "a", "list", "of", "strings"]
    
    #Example of using a template to render HTML
    #"Test" is a variable that we declare that will be passed to the HTML template. We can call that whatever we want.
    return render_template('placeholder.html', test = my_variable, a_number = 3, loopable_list = my_list)
    
@app.route('/TestForm')
def test():
    return render_template('testform.html', my_form = TestForm())



@app.route('/')
def login():
    return render_template('login.html')

@app.route('/calendar')
def calendar():
    return render_template('calendar.html')

app.run(host='0.0.0.0', port=8080)
