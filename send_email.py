import boto3

aws_access_key_id = ''
aws_secret_access_key = ''

client = boto3.client(service_name='ses',
                        aws_access_key_id= aws_access_key_id,
                        aws_secret_access_key= aws_secret_access_key
)

response = client.list_identities()

print(response)

# dest_address = 
# src_address = 
# subject =
# body =

# # verify

# response = client.verify_email_identity(
#     EmailAddress=dest_address
# )

# # send email

# response = client.send_email(
#         Destination={
#             "ToAddresses": [
#                 dest_address,
#             ],
#         },
#         Message={
#             "Body": {
#                 "Text": {
#                     body,
#                 }
#             },
#             "Subject": {
#                 subject,
#             },
#         },
#         Source=src_address,
#     )