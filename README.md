# ToDo
Install:

1. Clone the Github Repository.
2. Change to the directory ~/ToDo/
3. Install a virtual Python Enviroment: $ python -m virtualenv env
4. Activate the virtualenv:$ source env/bin/activate
5. Install packages: pip install -r requirements.txt
6. Install mongodb:  apt-get install mongodb or sudo apt-get install mongodb
7. Start its daemon process: mongod
    Maybe you will have to specify another port, if default 27017 is already in use:
        sudo /etc/init.d/mongodb stop
        mongod --port <port_number>
        sudo /etc/init.d/mongodb start
    Some configuration of the server, including the ports, is available: 
        in line 10 - server port, in line 11 - DB port, in line 13 names of
        the database and the collection, which will be created in MongoDB.
8. Test mongo shell: mongo
9. Quit mongo shell: exit
10. Start todo: python3 app.py
11. How to use it with curl is shown lower. It also usable with browser: 127.0.0.1:5000


Use the API with curl:

Create a new item:
    curl -X PUT -d '{"name": "<name>",
    "description": "<description>",
    "date_deadline": "<YYYY-MM-DD>",
    "tags": [<tag1>, <tag2>, ..., <tagn>]}' "127.0.0.1:5000/create"
All parameter in the json are optional. Attribute _id will be set by Mongo DB and date_created by the server. 

List all items:
    curl -X GET -d '{}' "127.0.0.1:5000/ls"
List some special set of items (examples):
    curl -X GET -d '{"name": "nameless"}' "127.0.0.1:5000/ls" # lists all items with name "nameless"
    curl -X GET -d '{"tags: ["bla"]"}' "127.0.0.1:5000/ls" # lists with tag "bla"
    curl -X GET -d '{"tags": ["blas", "das"]}' "127.0.0.1:5000/ls" # lists every item with one of the tags
"ls" corresponds with "db.collection.find({...}) in MongoDB. Works for all six attributes.

View a specific item:
    curl -X GET "127.0.0.1:5000/view/<_id>"

Delete a specific item:
    curl -X DELETE "127.0.0.1:5000/delete/<_id>"

Delete many items:
    curl -X DELETE -d {...} "127.0.0.1:5000/delete" # deletes a specified by the json -d
    curl -X DELETE -d {} "127.0.0.1:5000/delete" # empty json -> delete all
Works like "ls". Corresponds to db.collection.deleteMany({...}) in MongoDB. 
