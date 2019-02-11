from flask import Flask, request, render_template, redirect, url_for
from helpers import *
from datetime import datetime
from bson.objectid import ObjectId
from dateutil.parser import parse as time_parse
from argparse import ArgumentError
from pprint import pprint
from json import loads, dumps

flask_params = {"port": 5000}
db_params = {"port": 27017, "host": "localhost"}
db = db_helper(db_params)
db_names = {"database": "todo", "collection": "items"}
view_template = 'created.html'
main_template = 'hello.html'
head_template = 'head.html'
table_template = 'table.html'

app = Flask(__name__)


def ls_html(args={}, **kwargs):
    feedback = list(db.find(args, **db_names))
    ret = render_template(head_template, **kwargs) + render_template(table_template, rows=feedback)
    return ret

#--------------------------------------------------------------------SERVER-----------
@app.route('/', methods=['GET'])
def main_page():
    return ls_html()

@app.route('/ls', methods=['GET'])
def ls():
    args = request.get_json(force=True)
    feedback = db.find(args, **db_names)
    return dumps(feedback)

@app.route('/create', methods=['PUT'])
def create():
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
    args = request.get_json(force=True)
    feedback = db.delete_many(args, **db_names)
    return str(feedback.acknowledged)

@app.route('/delete/<string:_id>', methods=['DELETE'])
def delete_one(_id):
    return str(db.delete_many({'_id': ObjectId(_id)}, **db_names).acknowledged)

@app.route('/view/<string:_id>', methods=['GET'])
def view(_id):
    return dumps(db.find_one({'_id': ObjectId(_id)}, **db_names))
    
#--------------------------------------------Server HTMLs------------------------------------------------------------------------

@app.route('/', methods=['POST'])
def post(command=None):
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
