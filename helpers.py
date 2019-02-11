from argparse import ArgumentParser
from shlex import split as sh_split
from pymongo import MongoClient as db_client
from bson.objectid import ObjectId


def parse_arguments(args=None):
    parser = ArgumentParser()
    parser.add_argument("command", type=str)
    if "-i" in args or "--id" in args:
        parser.add_argument("-i", "--id", type=str, required=False, dest="_id", default=None)
    if "-n" in args or "--name" in args:
        parser.add_argument("-n", "--name", type=str, required=False, dest="name", default=None)
    if "-desc" in args or "--description" in args:
        parser.add_argument("-desc", "--description", type=str, required=False, dest="description", default=None)
    if "-dc" in args or "--date_created" in args:
        parser.add_argument("-dc", "--date_created", type=str, required=False, dest="date_created", default=None)
    if "-dd" in args or "--date_deadline" in args:
        parser.add_argument("-dd", "--date_deadline", type=str, required=False, dest="date_deadline", default=None)
    if "-t" in args or "--tags" in args:
        parser.add_argument("-t", "--tags", nargs="*", required=False, dest="tags")
    if isinstance(args, str):
        args = sh_split(args)
    args = vars(parser.parse_args(args))
    command = args.pop("command")
    return command, args

class db_helper:

    def __init__(self, db_params):
        self.insert_one = self.db_closure(self.insert_one, db_params)
        self.delete_many = self.db_closure(self.delete_many, db_params)
        self.find = self.db_closure(self.find, db_params)
        self.find_one = self.db_closure(self.find_one, db_params)

    def insert_one(self, client, diction, database, collection):
        if "_id" in diction:
            del diction["_id"]
        return client[database][collection].insert_one(diction)

    def delete_many(self, client, diction, database, collection):
        if "_id" in diction:
            diction["_id"] = ObjectId(diction["_id"])
        if "tags" in diction:
           self.cast_tags(diction)
        return client[database][collection].delete_many(diction)

    def find(self, client, diction, database, collection):
        if "_id" in diction:
            diction["_id"] = ObjectId(diction["_id"])
        if "tags" in diction:
           self.cast_tags(diction)
        items = list(client[database][collection].find(diction))
        for item in items:
            item['_id'] = str(item['_id'])
        return items

    def find_one(self, client, diction, database, collection):
        if "_id" in diction:
            diction["_id"] = ObjectId(diction["_id"])
        if "tags" in diction:
           self.cast_tags(diction)
        item = client[database][collection].find_one(diction)
        if item:
            item['_id'] = str(item['_id'])
        return item
    
    def cast_tags(self, diction):
        tags = diction['tags']
        diction["$or"] = [{"tags": {"$eq": tag}} for tag in tags]
        del diction["tags"]
        return diction

    def db_closure(self, function, db_params):
        def db_function(*args, **kwargs):
            client = db_client(**db_params)
            try:
                feedback = function(client, *args, **kwargs)
            finally:
                client.close()
            return feedback
        return db_function

