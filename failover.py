import boto3
import datetime
import requests

client = boto3.client('lambda')
url = "https://api.itsag1t1.com/health"
region = 'ap-southeast-1'

response = requests.get(url)
data = response.json()
print(data)

current_status = 'ok'
prev_status = 'ok'

print("--CHANGED STATUS TO FAIL--")
response = client.update_function_configuration(
    FunctionName='health_check',
    Environment={
        'Variables': {
            'STATUS': 'fail'
        }
    }
)

start_time = datetime.datetime.now()
print("...")

while True:
    response = requests.get(url)
    data = response.json()

    if data['status'] != prev_status:
        print(data)
        prev_status = current_status
        current_status = data['status']

    if data['region'] != 'ap-southeast-1':
        break

response = requests.get(url)
data = response.json()
print(data)

end_time = datetime.datetime.now()
time_diff = end_time - start_time
print(f'FAILOVER DURATION: {time_diff}')

response = client.update_function_configuration(
    FunctionName='health_check',
    Environment={
        'Variables': {
            'STATUS': 'ok'
        }
    }
)

print("--CHANGED STATUS TO OK--")
