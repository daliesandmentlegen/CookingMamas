from flask import render_template, url_for, request, redirect, session
from application.dataAccess import get_recipe_by_id, get_dietary_types, get_allergy_types, get_tool_names, \
    get_ingredient_names, get_unit_types, get_recipe_title, get_recipe_desc, get_cuisine_types, get_duration
from application import app


@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html', title='Home')


@app.route('/welcome/<name>')
def welcome(name):
    return render_template('welcome.html', name=name, group='Everyone')


@app.route('/about/<name>')
@app.route('/about')
def about(name):
    return render_template('about.html', name=name.capitalize(), colour=['red', 'yellow', 'green'])


@app.route('/login', methods=['GET', 'POST'])
def login():
    # app.logger.debug("Start of login")
    if request.method == 'POST':
        session['username'] = request.form['username']
        # app.logger.debug("Username is: " + session['username'])
        session['loggedIn'] = True
        session['role'] = 'admin'
        return redirect(url_for('all_products'))
    return render_template('login.html', title="Login")


@app.route('/recipe/<int:recipe_id>')
def recipe(recipe_id):
    recipes = get_recipe_by_id(recipe_id)
    return render_template('recipe.html', recipe=recipes)


# TO DO Create the route that will help populate the options for the database form
# Also to submit the data to the database - stored procedure?
@app.template_filter('format_timedelta')
def format_timedelta_filter(value):
    if value is None:
        return ''  # Or any other default value you prefer

    hours, remainder = divmod(value.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return '{:02}:{:02}:{:02}'.format(hours, minutes, seconds)


@app.route('/submitrecipepage1', methods=['GET','POST'])
def submitrecipepage1():
    # uses the function in data access to get the list of dietary types and assigns to variable dietary type
    cuisinetype = get_cuisine_types()
    durationdata = get_duration()
    if request.method == 'POST':
        # Get data from page 1 form and store in session
        session['recipeName'] = request.form['recipeName']
        session['recipeDescription'] = request.form['recipeDescription']
        session['cuisine'] = request.form.getlist('cuisine')
        session['duration'] = request.form.getlist('duration')
        session['serving'] = request.form['serving']
        return redirect(url_for('submitrecipepage2'))
    return render_template('submitRecipepage1.html', title='Recipe', cuisinetype = cuisinetype, durationdata = durationdata)


# the sessions are meant to save the data submitted on the form page so that when we get to the end of the form we can then take that data and use it
@app.route('/submitrecipepage2', methods=['GET', 'POST'])
def submitrecipepage2():
    # uses the function in data access to get the list of dietary types and assigns to variable dietary type
    dietarytype = get_dietary_types()
    allergytype = get_allergy_types()
    toolname = get_tool_names()
    if request.method == 'POST':
        # Get data from page 1 form and store in session
        session['dietary'] = request.form.getlist('dietary')
        session['allergytype'] = request.form.getlist('allergytype')
        session['toolname'] = request.form.getlist('toolname')
        return redirect(url_for('submitrecipepage3'))
    return render_template('submitRecipepage2.html', title='Recipe', dietarytype=dietarytype, allergytype=allergytype,
                           toolname=toolname)


# page 3 for ingredients
# not currently displaying the ingredients once supposedly added
# got myself all confused by the sessions so between 3 and add recipe needs more thought
@app.route('/submitrecipepage3', methods=['GET', 'POST'])
def submitrecipepage3():
    ingredientname = get_ingredient_names()
    unitname = get_unit_types()
    addedingredients = session.get('addedingredients', [])
    if request.method == 'POST':
        ingredient = request.form.getlist('ingredientname')
        quantity = request.form['quantity']
        unit = request.form.getlist('unitname')
        new_ingredient = {
            'ingredient': ingredient,
            'quantity': quantity,
            'unit': unit
        }

        addedingredients.append(new_ingredient)
        session['addedingredients'] = addedingredients

        return redirect(url_for('submitrecipepage4'))
    return render_template('submitRecipepage3.html', title='Recipe', ingredientname=ingredientname, unitname=unitname, addedingredients = addedingredients )

# add recipe and submit page 3 are currently not achieving the goal of adding to the table
# need to rethink it and work out how to make it work so it does add to the table each time
# also add recipe page has massive buttons so needs some styling!
@app.route('/addrecipe', methods=['GET', 'POST'])
def addingredients():
    ingredientname = get_ingredient_names()
    unitname = get_unit_types()

    # Initialize 'addedingredients' in session if not already initialized
    if 'addedingredients' not in session:
        session['addedingredients'] = []
    if request.method == 'POST':
        # Get data from page 2 form and store in session
        ingredient = request.form.get('ingredientname')
        quantity = request.form.get('quantity')
        unit = request.form.get('unitname')
        newingredients = {
            'ingredient': ingredient,
            'quantity': quantity,
            'unit': unit
        }

        session['addedingredients'].append(newingredients)
        return redirect(url_for('submitrecipepage3'))
    # addedingredients = []
    return render_template('addrecipe.html', title='Recipe', ingredientname=ingredientname, unitname=unitname)


# page 4 for steps
@app.route('/submitrecipepage4', methods=['GET', 'POST'])
def submitrecipepage4():
    # uses the function in data access to get the list of dietary types and assigns to variable dietary type
    if request.method == 'POST':
        # Get data from page 2 form and store in session
        session['step'] = request.form.getlist('step')
        # Process and save data
        final_data = {
            'data1': session.pop('data1', None),
            'data2': session.pop('data2', None),
            'data3': session.pop('data3', None)
        }
        # placeholder for calling the sql procedures:
        # cursor.callproc('xx', args)
        # db.commit()
        return redirect(url_for('successsubmit'))
    return render_template('submitRecipepage4.html', title='Recipe')

@app.route('/submitsuccess')
def successsubmit():
    return render_template('submitRecipeSuccess.html', title='Success')


@app.route('/search')
def search():
    recipename = get_recipe_title()
    recipedesc = get_recipe_desc()
    ingredientname = get_ingredient_names()
    return render_template('search.html', recipename=recipename, recipedesc=recipedesc, ingredientname=ingredientname)



