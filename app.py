from flask import Flask, request, render_template
from helpers import *
from datetime import datetime
from bson.objectid import ObjectId
from dateutil.parser import parse as time_parse
from argparse import ArgumentError

flask_params = {"port": 5000}
db_params = {"port": 27017, "host": "localhost"}
db = db_helper(db_params)
db_names = {"database": "todo", "collection": "items"}
view_template = 'created.html'
main_template = 'hello.html'
head_template = 'head.html'
table_template = 'table.html'

app = Flask(__name__)


def _list(args={}, **kwargs):
    feedback = list(db.find(args, **db_names))
    ret = render_template(head_template, **kwargs) + render_template(table_template, rows=feedback)
    return ret


@app.route('/', methods=['GET'])
def main_page():
    return _list()


@app.route('/', methods=['POST'])
def post():
    command = request.form.get('command')
    if not command:
        return _list(head='Empty Command')

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
            return _list(head=str(e))

    if "create" == command:
        args['date_created'] = str(datetime.now().date())
        if '_id' in args:
            del args['_id']
        feedback = db.insert_one(args, **db_names)
        if feedback.acknowledged:
            return _list(head='Created'+' '+str(args['_id']))
        else:
            return _list(head='Creating failed')

    if "tags" in args:
        tags = args['tags']
        args["$or"] = [{"tags": {"$eq": tag}} for tag in tags]
        del args["tags"]

    if "delete" == command:
        feedback = db.delete_many(args, **db_names)
        if feedback.acknowledged:
            return _list(head='Deleted')
        else:
            return _list(head='Deleting failed')

    if "list" == command:
        return _list(args)

    if "view" == command:
        feedback = db.find_one(args, **db_names)
        list_feedback = list(db.find({}, **db_names))
        return render_template(head_template, head="view") + render_template(view_template, **feedback) + render_template(table_template, rows=list_feedback)

    if "help" == command:
        list_feedback = list(db.find({}, **db_names))
        return render_template(head_template) + render_template(main_template) + render_template(table_template, rows=list_feedback)

    return main_page()

if __name__ == '__main__':
    app.run(**flask_params)
