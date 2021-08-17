
import boto3
import time
import uuid

s3 = boto3.client('s3')
dynamodb = boto3.client('dynamodb')
rekognition = boto3.client('rekognition')


def lambda_handler(event, context):

    utime = str(int(time.time())) #Current Unix Time   
 
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']  
    image = {
        'S3Object': {
            'Bucket': bucket,
            'Name': key,
            }
        }
        
    response = rekognition.detect_protective_equipment(Image=image)
    
    print(response)
    persons = response['Persons']
    for person in persons:
        
        if person['BodyParts']:
            
            bodyPart = person['BodyParts'][0]
            
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

