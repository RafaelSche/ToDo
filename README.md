# ToDo
Install:

1. Clone the Github Repository.
2. Change to the directory ~/ToDo/
3. Install a virtual Python Enviroment: $ python -m virtualenv env
4. Activate the virtualenv:$ source env/bin/activate
5. Install packages: pip install -r requirements.txt
6. Leave the enviroment
5. Install mongodb:  apt-get install mongodb or sudo apt-get install mongodb
7. Start its daemon process: mongod
    Maybe you will have to specify another port, if default 27017 is already in use:
        sudo /etc/init.d/mongodb stop
        mongod --port <port_number>
        sudo /etc/init.d/mongodb start
8. Test mongo shell: mongo
9. Quit mongo shell: exit
10. Start todo: bash todo or ./todo
11. Open 127.0.0.1:5000/ and print help in the command field
