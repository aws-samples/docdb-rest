"""
  Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.

  Licensed under the Apache License, Version 2.0 (the "License").
  You may not use this file except in compliance with the License.
  A copy of the License is located at

      http://www.apache.org/licenses/LICENSE-2.0

  or in the "license" file accompanying this file. This file is distributed
  on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
  express or implied. See the License for the specific language governing
  permissions and limitations under the License.
"""
import json
import boto3
import os
import ast
import pymongo
import bson
import datetime
## GLOBALS
db_client = None
db_secret_name = os.environ['DB_SECRET_NAME']
pem_locator ='/opt/python/rds-combined-ca-bundle.pem'
datetime_str = "%Y-%m-%dT%H:%M:%S"
## HELPERS
def stringify(doc):
    if (type(doc) == str):
        return doc
    if (type(doc) == dict):
        for k, v in doc.items():
            doc[k] = stringify(v)
    if (type(doc) == list):
        for i in range(len(doc)):
            doc[i] = stringify(doc[i])
    if (type(doc) == bson.ObjectId):
        doc = str(doc)
    if (type(doc) == datetime.datetime):
        doc = doc.strftime(datetime_str)
    return doc
## DOCUMENTDB CREDENTIALS
def get_credentials():
    """Retrieve credentials from the Secrets Manager service."""
    boto_session = boto3.session.Session()
    try:
        secrets_client = boto_session.client(service_name='secretsmanager', region_name=boto_session.region_name)
        secret_value = secrets_client.get_secret_value(SecretId=db_secret_name)
        secret = secret_value['SecretString']
        secret_json = json.loads(secret)
        username = secret_json['username']
        password = secret_json['password']
        host = secret_json['host']
        port = secret_json['port']
        return (username, password, host, port)
    except Exception as ex:
        raise
## DOCUMENTDB CONNECTION
def get_db_client():
    """Return an authenticated connection to DocumentDB"""
    # Use a global variable so Lambda can reuse the persisted client on future invocations
    global db_client
    if db_client is None:
        try:
            (username, password, docdb_host, docdb_port) = get_credentials()
            db_client = pymongo.MongoClient(host=docdb_host, port=docdb_port, ssl=True, ssl_ca_certs=pem_locator, replicaSet='rs0', connect = True)
            db_client.admin.command('ismaster')
            db_client["admin"].authenticate(name=username, password=password)
        except Exception as ex:
            raise
    return db_client
## Extract the db.collection from event and return collection
def collection_from_event(event):
    path = event["path"].rstrip("/")
    print("path: " + path)
    splits = path.split("/")
    collection_name = splits[-1]
    db_name = splits[-2]
    get_db_client()
    print("db_name: " + db_name + "; collection_name: " + collection_name)
    db = db_client[db_name]
    collection = db[collection_name]
    return collection
## Hanlde DELETE
def handle_delete(event):
    collection = collection_from_event(event)
    body = json.loads(event["body"])
    filter = None
    if "filter" in body.keys():
        filter = body["filter"]
    print(filter)
    res = collection.delete_many(filter)
    return stringify(res.raw_result)
## Hanlde PATCH
def handle_patch(event):
    collection = collection_from_event(event)
    filter = None
    update = None
    body = json.loads(event["body"])
    print(event["body"])
    print(body)
    if "filter" in body.keys():
        filter = body["filter"]
    if "update" in body.keys():
        update = body["update"]
    print(filter)
    print(update)
    res = collection.update_many(filter, update)
    return stringify(res.raw_result)
## Hanlde POST
def handle_post(event):
    collection = collection_from_event(event)
    body = json.loads(event["body"])
    print(body)
    collection.insert_one(body)
    return stringify(body)
## Handle GET
def handle_get(event):
    collection = collection_from_event(event)
    input_qs = event["queryStringParameters"]
    filter = None
    projection = None
    sort = None
    limit = 0
    skip = 0
    if None != input_qs:
        if "filter" in input_qs.keys():
            filter = json.loads(input_qs["filter"])
        if "projection" in input_qs.keys():
            projection = json.loads(input_qs["projection"])
        if "sort" in input_qs.keys():
            sort = ast.literal_eval(input_qs["sort"])
        if "limit" in input_qs.keys():
            limit = int(input_qs["limit"])
        if "skip" in input_qs.keys():
            skip = int(input_qs["skip"])

    print(filter)
    res = list(collection.find(filter=filter, projection=projection, sort=sort, limit=limit, skip=skip))
    return stringify(res) 

# Lambda Handler
def lambda_handler(event, context):
    print(event)
    httpMethod = event["httpMethod"]
    retval = "Done"
    if "GET" == httpMethod:
        retval = handle_get(event)
    elif "PUT" == httpMethod:
        retval = handle_post(event)
    elif "POST" == httpMethod:
        retval = handle_post(event)
    elif "PATCH" == httpMethod:
        retval = handle_patch(event)
    elif "DELETE" == httpMethod:
        retval = handle_delete(event)
    print(retval)

    return {
        'statusCode': 200,
        'body': json.dumps(retval)
    }
