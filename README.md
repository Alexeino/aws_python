# Running Grid Maker through lambda

## Create a Role for Lambda to interact with S3
* In IAM console go to Roles and Create a role for lambda and allow access to s3 for this role.
* Replace your role arn in the lambda function creation command.

## Packaging code and dependencies
* pip install -r requirements.txt --target ./package 
* cd package ; zip -r ~/lambda-function.zip .
* cd .. ; zip ~/lambda-function.zip lambda_function.py

## Creating Lambda Function through AWS CLI
* aws lambda create-function \
 --function-name grid-maker \
 --runtime python3.9 \
 --timeout 30 \
 --handler lambda_function.lambda_handler \
 --role <lambda_role_arn> \
--zip-file fileb://~/lambda-function.zip

## Invoking Lambda Functio while passing event.json params as payload
* aws lambda invoke --payload fileb://event.json --function-name grid-maker ~/output.txt
This will run the lambda function if everything is alright