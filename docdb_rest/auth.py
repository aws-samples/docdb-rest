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
import os
import json
import base64

def lambda_handler(event, context):
  print(event)
  action = "Allow"
  authorization = None
  if "Authorization" in event["headers"]:
      authorization = event["headers"]["Authorization"]
  if "authorization" in event["headers"]:
      authorization = event["headers"]["authorization"]
  if None == authorization:
      action = "Deny"
  splits = base64.b64decode(authorization.split(" ")[-1]).decode("utf-8").split(":")
  username = splits[0]
  password = splits[1]
  if (username != os.environ["USERNAME"] or password != os.environ["PASSWORD"]):
      print("Invalid username or password")
      action = "Deny"

  return buildPolicy(event, username, action)

def buildPolicy(event, principalId, action):
  methodArn = event["methodArn"]
  splits = methodArn.split(":")
  awsRegion = splits[3]
  awsAccountId = splits[4]
  apisplits = splits[5].split("/")
  restApiId = apisplits[0]
  apiStage = apisplits[1]
  apiArn = "arn:aws:execute-api:" + awsRegion + ":" + awsAccountId + ":" + restApiId + "/" + apiStage + "/*/*"

  policy = {
      "principalId": principalId,
      "policyDocument": {
          "Version": "2012-10-17",
          "Statement": [
              {
                  "Action": "execute-api:Invoke",
                  "Effect": action,
                  "Resource": [apiArn]
              }
          ]
      }
  }
  print(policy)
  return policy
