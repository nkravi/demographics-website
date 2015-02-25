"""
Contains code for web app twitter demographics
"""
from flask import Flask
from flask import render_template
from flask import request
import ConfigParser
from pymongo import MongoClient

app = Flask(__name__)

def debug(message):
  print message

"""
<get_conn>
Given the database name and collection name
returns a connection object

db_name-> name of the db
collection_name-> name of the collection

returns-> 
  success-> connection object
  failure-> None
"""
def get_conn(db_name,collection_name):
  host_name = cp.get('credentials','host_name')
  port_num  = int(cp.get('credentials','port_num'))
  debug('openning DB connection from '+ host_name)
  client = MongoClient(host_name,port_num)   
  if client:
    db = client[db_name]
    collection = db[collection_name]
    return collection
  debug('DB connection failed!')
  return None

"""
<is_acct_processed>
Checks whether the given account is processed or not
uses 'is_processed' flag to check it

account-> name of the account to be checked 

returns->
   True or False
"""
def is_acct_processed(account):
  db_name = cp.get('db','name')
  accts   = cp.get('collections','accounts')
  conn    = get_conn(db_name,accts)
  data    = conn.find_one({"_id":account})
  if data and 'is_processed' in data:
      if data['is_processed']:
         return True
  return False

"""
<add_email>
Adds email-id of the user to notify once the account
has been processed

account->name of the  account
email->emai of a user

return->
 True
"""
def add_email(email,account):
  db_name = cp.get('db','name')
  accts   = cp.get('collections','accounts')
  conn    = get_conn(db_name,accts)
  conn.update({'_id':account},{'$addToSet':{'email':email}},True)
  return True

"""
<get_results>
Gets demographic results from database given the account

account-> name of the account

return->
 results or None
"""
def get_results(account):
  db_name = cp.get('db','name')
  results = cp.get('collections','results')
  conn    = get_conn(db_name,results)
  values  = conn.find_one({'_id':account})
  if values:
    return values 
  return None
 
@app.route('/')
def show_home():
  return render_template('home.html')

@app.route('/submit')
def submit_form():
  account = request.args.get('account','')  
  if is_acct_processed(account):
    results = get_results(account)
    print results
    return render_template('display.html',results=results)
  return render_template('error.html',account=account)

@app.route('/email')
def submit_email():
  account = request.args.get('account','')
  email   = request.args.get('email','')
  add_email(email,account)
  return render_template('home.html')

if __name__ == '__main__':
  #read config file
  cp = ConfigParser.RawConfigParser()  
  cp.read('mongo_config')
  #start server
  app.debug = True
  app.run()

