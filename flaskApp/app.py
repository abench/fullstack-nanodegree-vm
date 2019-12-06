from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

app = Flask(__name__)

def init_db():
    engine = create_engine('sqlite:///restaurantmenu.db')
    # Bind the engine to the metadata of the Base class so that the
    # declaratives can be accessed through a DBSession instance
    Base.metadata.bind = engine

    DBSession = sessionmaker(bind=engine)
    # A DBSession() instance establishes all conversations with the database
    # and represents a "staging zone" for all the objects loaded into the
    # database session object. Any change made against the objects in the
    # session won't be persisted into the database until you call
    # session.commit(). If you're not happy about the changes, you can
    # revert all of them back to the last commit by calling
    # session.rollback()
    session = DBSession()
    return session

db = init_db()

@app.route('/')
@app.route('/hello')
def hello():
    output = '<h1>Menu</h1>'
    restaurants = db.query(Restaurant).all()
    for restaurant in restaurants:
        output += '<h2>Restaurant  <i> {} </i> </h2>'.format(restaurant.name)
        items = db.query(MenuItem).filter_by(restaurant_id=restaurant.id)
        for item in items:
            output += '<h3> {} </h3>'.format(item.name)
            #output += '</br>'
            output += item.price
            output += '</br></br>'
            output += item.description
            output += '</br></br>'
    return output

@app.route('/restaurants/<int:restaurant_id>/')
def restaurantMenu(restaurant_id):
    output = '<h1>Restaurant</h1>'
    restaurant = db.query(Restaurant).filter_by(id=restaurant_id).one()
    output += '<h2> {} </h2>'.format(restaurant.name)
    items = db.query(MenuItem).filter_by(restaurant_id=restaurant.id)
    return render_template('menu.html', restaurant=restaurant, items=items)


# Task 1: Create route for newMenuItem function here

@app.route('/restaurants/<int:restaurant_id>/new/', methods=['GET', 'POST'])
def newMenuItem(restaurant_id):
    if request.method == 'POST':
        new_item = MenuItem(name=request.form['name'], restaurant_id = restaurant_id)
        db.add(new_item)
        db.commit()
        return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))
    else:
        return render_template('newmenuitem.html',restaurant_id=restaurant_id)


# Task 2: Create route for editMenuItem function here

@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/edit/', methods=['GET','POST'])
def editMenuItem(restaurant_id, menu_id):
    item_to_edit = db.query(MenuItem).filter_by(id=menu_id).one()
    if request.method == 'POST':
        item_to_edit.name = request.form['name']
        db.add(item_to_edit)
        db.commit()
        return redirect(url_for('restaurantMenu', restaurant_id = restaurant_id))

    else:
        return render_template('editmenuitem.html', restaurant_id = restaurant_id, item = item_to_edit )


# Task 3: Create a route for deleteMenuItem function here

@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/delete/', methods=['GET','POST'])
def deleteMenuItem(restaurant_id, menu_id):
    item_to_delete = db.query(MenuItem).filter_by(id=menu_id).one()
    if request.method == 'POST':
        db.delete(item_to_delete)
        db.commit()
        return redirect(url_for('restaurantMenu', restaurant_id=item_to_delete.restaurant_id))

    else:
        return render_template('deletemenuitem.html', item = item_to_delete)


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)

