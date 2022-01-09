import os
import io
import csv
from flask import Flask, Response, render_template, redirect, request, abort
from models import db, InventoryModel
from sqlalchemy import exc

# --------------------- CONFIGURING DB ---------------------

db_path = os.path.join(os.path.dirname(__file__), 'inventory.db')
db_uri = f"sqlite:///{db_path}"

app = Flask(__name__)

app.secret_key = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# --------------------- ENDPOINTS ---------------------


@app.before_first_request
def create_table():
    '''
    Create inventory.db before tool is initialized
    '''
    db.create_all()


@app.route('/', methods=['GET'])
def show_data():
    '''
    Shows all data on the main index.html page
    '''
    all_inventory = InventoryModel.query.all()
    if not all_inventory:
        return render_template('index.html', message="No data.")
    return render_template('index.html', data=all_inventory)


@app.route('/create/', methods=['GET', 'POST'])
def create():
    '''
    Create new item 
    '''
    if request.method == 'GET':
        return render_template('create.html')
    if request.method == 'POST':
        item_id = request.form['item_id']
        item_name = request.form['item_name']
        stock = request.form['stock']
        new_item = InventoryModel(
            item_id=item_id,
            item_name=item_name,
            stock=stock)
        db.session.add(new_item)
        db.session.commit()
        app.logger.info(f"Added item ${item_id}, ${item_name}...")
        return redirect('/')


@app.route('/search/', methods=['GET', 'POST'])
def search():
    '''
    Search for items
    '''
    if request.method == 'GET':
        found = InventoryModel.query.all()
        return render_template('search.html', data=found, message="")
    if request.method == 'POST':
        item_id = "{}%".format(request.form['item_id'])
        item_name = "{}%".format(request.form['item_name'])
        stock = "{}%".format(request.form['stock'])
        found = InventoryModel.query.filter(
            InventoryModel.item_id.like(item_id),
            InventoryModel.item_name.like(item_name),
            InventoryModel.stock.like(stock))

        message = ""
        if not found.first():
            message = "No matching items found."
        return render_template('search.html', data=found, message=message)


@app.route('/edit_delete/', methods=['GET', 'POST'])
def edit_delete():
    '''
    Edit/Delete intermediate page.
    This endpoint directs depending on edit or deletion
    '''
    # if page is accessed without first bypassing search page
    if request.method == 'GET':
        abort(400)
    if request.method == 'POST':
        item_id = int(request.form['item_all'])
        choice = request.form['edit_delete']
        found = InventoryModel.query.filter_by(
            item_id=item_id).first()

        if choice == "edit":
            return render_template('edit.html', selected=found)
        if choice == "delete":
            db.session.delete(found)
            db.session.commit()
            app.logger.info(
                f"Deleted item ${found.item_id}, ${found.item_name}...")
            return redirect('/')


@app.route('/edit/', methods=['GET', 'POST'])
def edit():
    '''
    Edits item
    '''
    if request.method == 'GET':
        abort(400)
    if request.method == 'POST':
        item_id = request.form['item_id']
        item_name = request.form['item_name']
        stock = request.form['stock']

        found = InventoryModel.query.filter_by(item_id=item_id).first()
        found.item_name = item_name
        found.stock = stock
        db.session.commit()
        app.logger.info(f"Edited item ${item_id}...")
        return redirect('/')


@app.route('/download/', methods=['GET'])
def download():
    '''
    Creates CSV and download link to CSV
    '''
    all_data = InventoryModel.query.all()
    output = io.StringIO()
    writer = csv.writer(output)

    # write fields
    fields = ['Item ID', 'Item Name', 'Stock']
    writer.writerow(fields)

    # write rows
    for item in all_data:
        writer.writerow([str(item.item_id), str(
            item.item_name), str(item.stock)])

    output.seek(0)
    return Response(output,
                    mimetype="text/csv",
                    headers={"Content-Disposition": "attachment;filename=inventory.csv"})

# --------------------- ERROR HANDLING ---------------------


@app.errorhandler(exc.IntegrityError)
def conflict(e):
    db.session.rollback()
    message = "Error 409: Conflict - This ID already exists. Choose another."
    app.logger.info("Error 409...")
    return render_template('message.html', message=message), 409


@app.errorhandler(400)
def bad_request(e):
    message = "Error 400: Bad Request."
    app.logger.info("Error 400...")
    return render_template('message.html', message=message), 400


@app.errorhandler(404)
def page_not_found(e):
    message = "Error 404: Page does not exist."
    app.logger.info("Error 404...")
    return render_template('message.html', message=message), 404


@app.errorhandler(500)
def internal_error(e):
    message = "Error 500: Internal error."
    app.logger.info("Error 500...")
    return render_template('message.html', message=message), 500
