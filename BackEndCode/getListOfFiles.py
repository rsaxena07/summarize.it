import json
import pymysql
import sys
import logging
import os


def lambda_handler(event, context):
    userEmail = event['context']['email']
    rds_host = "database-1.c8azeqy71oy4.us-west-1.rds.amazonaws.com"
    name = os.environ['dbUserName']
    password = os.environ['dbPassword']
    db_name = "SummarizeItDB"
    outputData = []

    # establish connection with rds
    try:
        conn = pymysql.connect(rds_host, user=name,
                               passwd=password, db=db_name, connect_timeout=5)
    except pymysql.MySQLError as e:
        logging.error(
            "ERROR: Unexpected error: Could not connect to MySQL instance.")
        logging.error(e)
        sys.exit()

    with conn.cursor() as cur:
        sql = "select user_given_name, file_creation_date from files where user_id ='" + userEmail + "'"
        cur.execute(sql)
        for name, date in cur.fetchall():
            outputData.append({'document': name, 'date': date.strftime(
                "%Y-%m-%d %H:%M:%S"), 'download': "null"})

    return {
        'statusCode': 200,
        'headers': {
            "Access-Control-Allow-Credentials": 'true',
            'Access-Control-Allow-Headers': "Access-Control-Allow-Origin, X-Requested-With, Content-Type, Accept, Authorization, Access-Control-Allow-Headers",
            "Access-Control-Allow-Origin": "*"

        },
        'body': json.dumps(outputData)
    }
