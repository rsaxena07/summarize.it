import json
import boto3
import datetime
import pymysql
import sys
import logging


def lambda_handler(event, context):
    # bucket name refers to the s3 bucket where files will be stored
    bucket_name = "text-files-uci-summarize-it"

    userEmail = event['context']['email']
    #userEmail = 'jashSohni@gmail.com'

    textData = event['body-json']['input_data']
    #textData = "this is a test text"

    userGivenName = event['body-json']['file_name']
    #userGivenName = 'shouldNotCome'

    timeNow = datetime.datetime.now()
    currentTimeStamp = timeNow.strftime("%m:%d:%Y%H:%M:%S")
    rds_host = "database-1.c8azeqy71oy4.us-west-1.rds.amazonaws.com"
    name = "admin"
    password = "Fastrack007"
    db_name = "SummarizeItDB"

    # establish connection with rds
    try:
        conn = pymysql.connect(rds_host, user=name,
                               passwd=password, db=db_name, connect_timeout=5)
    except pymysql.MySQLError as e:
        logger.error(
            "ERROR: Unexpected error: Could not connect to MySQL instance.")
        logger.error(e)
        sys.exit()

    # path will eventually have path of directory where file will be stored
    path = "users/"

    # encode this text
    encoded_string = textData.encode("utf-8")

    path += userEmail.replace('@', '') + "/"

    fileName = userGivenName + "_" + currentTimeStamp + ".txt"

    s3 = boto3.resource("s3")

    # to store file into the s3
    s3.Bucket(bucket_name).put_object(Key=path + fileName,
                                      Body=encoded_string, ContentDisposition='attachment')
    with conn.cursor() as cur:
        sql = "insert into files(user_id, user_given_name, name_in_storage, file_creation_date) Values (%s, %s, %s, %s)"
        val = (userEmail, userGivenName, fileName, timeNow)
        cur.execute(sql, val)

    conn.commit()

    return {
        'statusCode': 200,
        'headers': {
            "Access-Control-Allow-Credentials": 'true',
            'Access-Control-Allow-Headers': "Access-Control-Allow-Origin, X-Requested-With, Content-Type, Accept, Authorization, Access-Control-Allow-Headers",
            "Access-Control-Allow-Origin": "*"

        },
        'body': json.dumps("successful")
    }
