#!/usr/bin/env python2.7

"""
Columbia W4111 Intro to databases
Example webserver
To run locally
    python server.py
Go to http://localhost:8111 in your browser
A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""

import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)


DB_USER = "hw2846"
DB_PASSWORD = "414526344"
DB_SERVER = "w4111.cisxo09blonu.us-east-1.rds.amazonaws.com"

DATABASEURI = "postgresql://"+DB_USER+":"+DB_PASSWORD+"@"+DB_SERVER+"/proj1part2"

#
# This line creates a database engine that knows how to connect to the URI above
#
engine = create_engine(DATABASEURI)


# Here we create a searchInDrivers table and insert some values in it
engine.execute("""DROP TABLE IF EXISTS searchInDrivers;""")
engine.execute("""CREATE TABLE IF NOT EXISTS searchInDrivers (
  id serial,
  name text
);""")
# engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")

engine.execute("""DROP TABLE IF EXISTS searchInVehicles;""")
engine.execute("""CREATE TABLE IF NOT EXISTS searchInVehicles (
  id text,
  name text
);""")



@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request
  The variable g is globally accessible
  """
  try:
    g.conn = engine.connect()
  except:
    print("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to e.g., localhost:8111/foobar/ with POST or GET then you could use
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: http://flask.pocoo.org/docs/0.10/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def home():
  """
  request is a special object that Flask provides to access web request information:
  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments e.g., {a:1, b:2} for http://localhost?a=1&b=2
  See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
  """

  
  cursor = g.conn.execute("SELECT plate_number, time, city, on_street, cross_street, out_street, injured, death FROM Happen, Counted, Exist, Locations, Explains, Results WHERE Counted.collision_id = Happen.collision_id AND Exist.collision_id = Counted.collision_id AND Exist.coordinate = Locations.coordinate AND Explains.collision_id = Counted.collision_id AND Explains.rid = Results.rid ORDER BY time DESC LIMIT 10")
  
  users = []
  for result in cursor:
    users.append(result)

  cursor.close()

  context = dict(data = users)

  # Flask uses Jinja templates, which is an extension to HTML where you can
  # pass data to a template and dynamically generate HTML based on the data
  # (you can think of it as simple PHP)
  # documentation: https://realpython.com/blog/python/primer-on-jinja-templating/
  #
  # You can see an example template in templates/index.html
  #
  # context are the variables that are passed to the template.
  # for example, "data" key in the context variable defined below will be 
  # accessible as a variable in index.html:
  #
  #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
  #     <div>{{data}}</div>
  #     
  #     # creates a <div> tag for each element in data
  #     # will print: 
  #     #
  #     #   <div>grace hopper</div>
  #     #   <div>alan turing</div>
  #     #   <div>ada lovelace</div>
  #     #
  #     {% for n in data %}
  #     <div>{{n}}</div>
  #     {% endfor %}
  #
  # render_template looks in the templates/ folder for files.
  # for example, the below file reads template/index.html
  #
  return render_template("base.html", **context)

#
# This is an example of a different path.  You can see it at
# 
#     localhost:8111/another
#
# notice that the functio name is another() rather than index()
# the functions for each app.route needs to have different names
#



# Example of adding new data to the database
@app.route('/add', methods=['POST'])
def add():
  name = request.form['name']
  print(name)
  cmd = 'INSERT INTO test(name) VALUES (:name1), (:name2)'
  g.conn.execute(text(cmd), name1 = name, name2 = name)
  return redirect('/')


# @app.route('/')
# def index():

#   # DEBUG: this is debugging code to see what request looks like
#   print(request.args)

#   cursor = g.conn.execute("SELECT name FROM test")
#   names = []
#   for result in cursor:
#     names.append(result['name'])  # can also be accessed using result[0]
#   cursor.close()

#   context = dict(data = names)

#   return render_template("index.html", **context)

# @app.route('/tool')
# def another():
#   print(request.args)

#   cursor = g.conn.execute("SELECT * FROM Users")
  
#   users = []
#   for result in cursor:
#     users.append(result)

#   cursor.close()

#   context = dict(data = users)

#   return render_template("tool.html", ** context)

@app.route('/tool')
def another():
  return render_template("tool.html")

@app.route('/stats')
def stats():
  return render_template("stats.html")

@app.route('/base')
def base():
  return redirect('/')

@app.route('/contact')
def contact():
  return render_template("contact.html")

@app.route('/searchInDrivers', methods=['POST'])
def searchInDrivers():
  userid = request.form['userid']
  print(userid)

  cmd = 'INSERT INTO searchInDrivers(id) VALUES (:userid)'
  g.conn.execute(text(cmd), userid = userid)

  cursor = g.conn.execute("SELECT Users.name, age, driving_age FROM Users, searchInDrivers WHERE Users.uid = searchInDrivers.id")
  
  users = []
  for result in cursor:
    users.append(result)

  cursor.close()

  context = dict(data_users = users)

  g.conn.execute("DELETE from searchInDrivers")

  return render_template("searchInDrivers.html", ** context)


@app.route('/searchInVehicles', methods=['POST'])
def searchInVehicles():
  plate_num = request.form['plate_num']
  print(plate_num)

  cmd = 'INSERT INTO searchInVehicles(id) VALUES (:plate_num)'
  g.conn.execute(text(cmd), plate_num = plate_num)

  cursor = g.conn.execute("SELECT plate_number, use_year FROM Vehicles, searchInVehicles WHERE Vehicles.plate_number = searchInVehicles.id")
  
  vehicles = []
  for result in cursor:
    vehicles.append(result)

  cursor.close()

  context = dict(data_vehicles = vehicles)

  g.conn.execute("DELETE from searchInVehicles")

  return render_template("searchInVehicles.html", ** context)


@app.route('/insert')
def insert():
  return render_template("insert.html")


if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using
        python server.py
    Show the help text using
        python server.py --help
    """

    HOST, PORT = host, port
    print("running on %s:%d" % (HOST, PORT))
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


  run()


