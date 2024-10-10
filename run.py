import base64

# Path to your Firebase Admin Key JSON
json_file_path = "imageria-a09ae-firebase-adminsdk-whbrs-cb68800962.json"

# Read the file and encode it
with open(json_file_path, "rb") as f:
    encoded_data = base64.b64encode(f.read())

# Convert bytes to string and print the Base64 string
base64_string = encoded_data.decode('utf-8')
print(base64_string)
