import json
import boto3
import pymysql
import sys
import logging


def create_presigned_url(key):
    """Generate a presigned URL to share an S3 object

    :param bucket_name: string
    :param object_name: string
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Presigned URL as string. If error, returns None.
    """

    # Generate a presigned URL for the S3 object
    s3_client = boto3.client('s3')
    try:
        response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': 'text-files-uci-summarize-it',
                                                            'Key': key},
                                                    ExpiresIn=3600)
    except ClientError as e:
        logging.error(e)
        return None

    # The response contains the presigned URL
    return response


def lambda_handler(event, context):
    key = 'users/'
    #key = 'users/amit.somani64gmail.com/Original_2020-11-2019:32:18.759406.txt'
    userEmail = event['context']['email']
    #userEmail = 'amit.somani64@gmail.com'
    key += userEmail.replace('@', '') + "/"
    documentName = event['body-json']['document_name']
    #documentName = 'NewTestDoc'
    timeStamp = event['body-json']['timestamp']
    #timeStamp = '2020-12-03 20:50:48'

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

    toGetFile = key

    with conn.cursor() as cur:
        sql = "select name_in_storage from files where user_id ='" + userEmail + \
            "' and user_given_name ='" + documentName + \
            "' and file_creation_date = '" + timeStamp + "';"
        cur.execute(sql)
        for name in cur.fetchall():
            toGetFile += name[0]

    # print(userEmail)
    # print(documentName)
    # print(timeStamp)
    response = create_presigned_url(toGetFile)
    #response = "hi"
    # print(response)

    return {
        'statusCode': 200,
        'headers': {
            "Access-Control-Allow-Credentials": 'true',
            'Access-Control-Allow-Headers': "Access-Control-Allow-Origin, X-Requested-With, Content-Type, Accept, Authorization, Access-Control-Allow-Headers",
            "Access-Control-Allow-Origin": "*"

        },
        'body': json.dumps(response)
    }
