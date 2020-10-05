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