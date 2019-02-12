"""
Functions to handle requests on the server are defined here.
Several of them require a json to specify items in the DB.
Items a stored in MongoDB as jsons, too.
A json matches to an item if one of the key-value pairs
a equal, as in MongoDB, too. 
"""

from flask import Flask, request, render_template, redirect, url_for
from helpers import *
from datetime import datetime
from bson.objectid import ObjectId
from dateutil.parser import parse as time_parse
from argparse import ArgumentError
from pprint import pprint
from json import loads, dumps

flask_params = {"port": 5000} # server port

db_params = {"port": 27017, "host": "localhost"} # db port and hostname
db = db_helper(db_params)
db_names = {"database": "todo", "collection": "items"} # names of database and collection

#  names of jinja2 templates 
view_template = 'created.html' # to show one specific item
main_template = 'hello.html'    # help page (not main)
head_template = 'head.html'     # top of all pages, contains the HTML POST form
table_template = 'table.html'   # table to list items

app = Flask(__name__)


def ls_html(args={}, **kwargs):
    """
    Helper function to list items in a table. args specifies which items to list. List all if args empty.
    """
    feedback = list(db.find(args, **db_names))
    ret = render_template(head_template, **kwargs) + render_template(table_template, rows=feedback)
    return ret

#--------------------------------------------------------------------SERVER-----------
@app.route('/', methods=['GET'])
def main_page():
    """
    main page: http://localhost:<port>
    returns the POST field and lists all items.
    """
    return ls_html()

@app.route('/ls', methods=['GET'])
def ls():
    """
    Handles GET request on http://localhost:<port>/ls
    Lists items. Which items to list can be specified by a json.
    Empty json to list all.
    A json matches to an item if one of the key-value pairs
    a equal
    return: json string (list of dictionaries)
    """
    args = request.get_json(force=True)
    feedback = db.find(args, **db_names)
    return dumps(feedback)

@app.route('/create', methods=['PUT'])
def create():
    """
    Handles PUT request on http://localhost:<port>/create
    Creates an item: attributes of the item should be specified with json.
    return: str (bool), True if succesful
    """
    args = request.get_json(force=True)
    args['date_created'] = str(datetime.now().date())
    if "date_deadline" in args:
        try:
            args["date_deadline"] = str(time_parse(args["date_deadline"]).date())
        except ValueError:
            return "date_deadline_format invalid; try YYYY-MM-DD or see dateutil.parser.parse\n"
    feedback = db.insert_one(args, **db_names)
    return str(feedback.acknowledged)

@app.route('/delete', methods=['DELETE'])
def delete():
    """
    Handles DELETE request on http://localhost:<port>/delete
    Deletes several items specified by a json.
    A json matches to an item if one of the key-value pairs
    a equal
    return: str(bool), True if succesful
    """
    args = request.get_json(force=True)
    feedback = db.delete_many(args, **db_names)
    return str(feedback.acknowledged)

@app.route('/delete/<string:_id>', methods=['DELETE'])
def delete_one(_id):
    """
    Handles DELETE request on http://localhost:<port>/delete/<_id>
    Deletes one item specified by its _id.
    param: _id
    return: str(bool), True if succesful
    """
    return str(db.delete_many({'_id': ObjectId(_id)}, **db_names).acknowledged)

@app.route('/view/<string:_id>', methods=['GET'])
def view(_id):
    """
    Handles DELETE request on http://localhost:<port>/view/<_id>
    returns  one item specified by its _id.
    param: _id
    return: json string (one dictionary), null if not found
    """
    return dumps(db.find_one({'_id': ObjectId(_id)}, **db_names))
    
#--------------------------------------------Server HTMLs------------------------------------------------------------------------

@app.route('/', methods=['POST'])
def post(command=None):
    """
    Handles POST request on the main_page. 
    """
    command = request.form.get('command')
    if not command:
        return ls_html(head='Empty Command')

    command, args = parse_arguments(command)

    if "_id" in args:
        if args['_id'] == "all":
            args = {}
        else:
            args['_id'] = ObjectId(args['_id'])

    if "date_deadline" in args:
        try:
            args["date_deadline"] = str(time_parse(args["date_deadline"]).date())
        except ValueError as e:
            return ls_html(head=str(e))

    if "create" == command:
        args['date_created'] = str(datetime.now().date())
        if '_id' in args:
            del args['_id']
        feedback = db.insert_one(args, **db_names)
        if feedback.acknowledged:
            return ls_html(head='Created'+' '+str(args['_id']))
        else:
            return ls_html(head='Creating failed')

    if "delete" == command:
        feedback = db.delete_many(args, **db_names)
        if feedback.acknowledged:
            return ls_html(head='Deleted')
        else:
            return ls_html(head='Deleting failed')

    if "ls" == command:
        return ls_html(args)

    if "view" == command:
        feedback = db.find_one(args, **db_names)
        if feedback is None:
            feedback = {'_id': 'does noch exist'}
        ls_html_feedback = list(db.find({}, **db_names))
        return render_template(head_template, head="view") + render_template(view_template, **feedback) + render_template(table_template, rows=ls_html_feedback)

    if "help" == command:
        ls_html_feedback = list(db.find({}, **db_names))
        return render_template(head_template) + render_template(main_template) + render_template(table_template, rows=ls_html_feedback)

    return main_page()

if __name__ == '__main__':
    app.run(**flask_params)
