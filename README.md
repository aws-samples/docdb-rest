# REST API for Amazon DocumentDB

## Introduction
This project will create a CRUD REST API for an existing
Amazon DocumentDB cluster. It will use Amazon API Gateway
and AWS Lambda functions to create the API, as well as 
use AWS Secrets Manager to manage credentials to the 
database.

This project contains a SAM template and source
code for the primary Lambda functions.

### Inputs
The following are the inputs to the SAM template:
- Prefix to prepend to resources
- Amazon DocumentDB identifier
- Username for Amazon DocumentDB (to be stored in Secrets Manager)
- Password for Amazon DocumentDB (to be stored in Secrets Manager)
- VPC Subnet for Amazon DocumentDB (for the AWS Lambda to be deployed)
- Security group for access to Amazon DocumentDB (for the AWS Lambda)
- Username to protect the API Gateway endpoints
- Password to protect the API Gateway endpoints

## Build
To package the zip file for the Lambda Layer run

```
make
```

or

```
make layer-pymongo.zip
```

To validate the SAM template run:

```
sam validate
```

To build the SAM template run:

```
sam build
```

or 

```
make build
```

## Deploy
To deploy, run

```
sam deploy --guided
```

or 

```
make sam
```

And follow the prompts.

The REST API root endpoint will be recorded in the output variable:
`APIRoot`

## Access
The HTTP endpoint is protected by username/password access, which is set
up using the supplied API username and API password. To access the you need
to supply the username password in the request.

The basic API is accessed at: `https://APIUSER:APIPASSWORD@APIROOT/{databaseName}/{collectionName}`

For example, to access the collection `myColl` in the database `myDb`
(and using the APIUSER as `apiuser` and APIPASSWORD as `apipassword`)
you would use `https://apiuser:apipassword@APIROOT/myColl/myDb`

This one endpoint will handle multiple REST calls, depending on the
HTTP verb used.

### GET
With the GET operation, you can issue a `find()` command. It takes the
following arguments (all of which are optional):

- `filter` : this is a filter clause in the MongoDB dialect. E.g., `filter={"a":1,"b":"two"}`
- `projection` : this is a projection clause in the MongoDB dialect. E.g., `projection={"_id":0,"a":1}`
- `sort` : this is a sort clause in the MongoDB dialect. E.g., `sort={"a":1,"b":-1}`
- `limit` : this is an integer and the number of results to return.
- `skip` : this is an integer and the number of results to skip before returning results.

### PUT and POST
The PUT and POST verbs will perform the same operation, a database insert. The body
of the HTTP request is the document to be stored in the database.

### PATCH
The PATCH verb will perform a database update operation. The filter and update operations
should be passed as a JSON document as the body of the request. The filter to use to identify
which documents should be updated is passed as the filter field of the body. The update 
itself is passed as the update field in the body of the request and is in the MongoDB
dialect.

For example, to update all rows that have `a` equal to `100`, and increment the value of `b`
by 10 and set the value of `c` to `three`, you would use the following as the body of the request:
```
{
  "filter": {"a":100},
  "update": {
	  "$inc": {
		  "b": 10
		}, 
		"$set": {
		  "c": "three"
		}
	}
}
```

### DELETE
The DELETE verb will perform a database delete operation. The filter should be passed as a 
JSON document as the body of the request. The filter to use to identify
which documents should be deleted is passed as the filter field of the body.

For example, to delete all documents with the value of `a` as 100, you would use
```
{
  "filter": {"a":100},
}
```

## Examples
For these examples, set the environment variables `APIUSER`, `APIPASSWORD`,
and `APIROOT` to the API user, password, and root, respectively. For example:
```
export APIUSER=XXXXX
export APIPASSWORD=YYYYY
export APIROOT=ZZZZZ
```

1. PUT some data
```
curl -X PUT -H "Content-Type: application/json" -d '{"name":"brian", "rating": 5}' https://$APIUSER:$APIPWD@$URLBASE/docdb/blog/test
curl -X PUT -H "Content-Type: application/json" -d '{"name":"joe", "rating": 5}' https://$APIUSER:$APIPWD@$URLBASE/docdb/blog/test
```

2. POST some data
```
curl -X POST -H "Content-Type: application/json" -d '{"name":"jason", "rating": 3}' https://$APIUSER:$APIPWD@$URLBASE/docdb/blog/test
```

3. GET all the data
```
curl -G https://$APIUSER:$APIPWD@$URLBASE/docdb/blog/test
```

4. GET the joe document
```
curl -G --data-urlencode 'filter={"name": "joe"}' https://$APIUSER:$APIPWD@$URLBASE/docdb/blog/test
```

5. GET just the name field
```
curl -G --data-urlencode 'filter={"name": "joe"}' --data-urlencode 'projection={"_id": 0, "name": 1}' https://$APIUSER:$APIPWD@$URLBASE/docdb/blog/test
```

6. PATCH the jason document
```
curl -X PATCH -H "Content-Type: application/json" -d '{"filter": {"name": "jason"},"update": {"$set": {"rating": 4}}}' https://$APIUSER:$APIPWD@$URLBASE/docdb/blog/test
```

7. DELETE the jason document
```
curl -X DELETE -H "Content-Type: application/json" -d '{"filter": {"name": "jason"}}' https://$APIUSER:$APIPWD@$URLBASE/docdb/blog/test
```

==============================================

Copyright 2020 Amazon.com, Inc. or its affiliates. All Rights Reserved.

SPDX-License-Identifier: MIT-0

