#AWS Lambda supports code for almost any type of application or backend services possible. 
#It manages and performs all of the necessary maintenance including server and operating systems, scaling, code monitoring, and logging.
#Lambda can be used to run code in response to events such as changes to data in Amazon Simple Storage Service (Amazon S3) bucket or an Amazon DynamoDB table. 
#In our application, images uploaded to the S3 bucket triggers the Lambda function. 

import boto3
import time
import uuid

# Initialize s3 object
s3 = boto3.client('s3')
# Initialize dynamodb instace
dynamodb = boto3.client('dynamodb')
#Initialize recognition object
rekognition = boto3.client('rekognition')


def lambda_handler(event, context):

    utime = str(int(time.time())) #Current Unix Time   
 
    # Setting up the image parameter
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']  
    image = {
        'S3Object': {
            'Bucket': bucket,
            'Name': key,
            }
        }
    
    # Makes the API call with image as parameter
    response = rekognition.detect_protective_equipment(Image=image)
    
    persons = response['Persons']
    
    # Parse the JSON response
    for person in persons:
        if person['BodyParts']:
            
            bodyPart = person['BodyParts'][0]
            
            #Populate  table
            if(bodyPart['Name'] =='FACE'):
                if bodyPart['EquipmentDetections']:
                    dynamodb.put_item(
                        TableName='Face_Covering',
                        Item={
                            'personID': {'S': str(uuid.uuid1())},
                            'confidence': {'S': str(bodyPart['EquipmentDetections'][0]['CoversBodyPart']['Confidence'])},
                            'date_time': {'S': str(utime)},
                            'face_cover': {'S': str(bodyPart['EquipmentDetections'][0]['CoversBodyPart']['Value'])}
                        })
                else:
                    dynamodb.put_item(
                        TableName='Face_Covering',
                        Item={
                            'personID': {'S': str(uuid.uuid1())},
                            'confidence': {'S': str('')},
                            'date_time': {'S': str(utime)},
                            'face_cover': {'S': str('False')}
                        })

