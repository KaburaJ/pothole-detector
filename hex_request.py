import requests
from PIL import Image

url = 'http://192.168.0.130:5000/detect_potholes'

text_file_path = 'test_images/sample1.txt'

with open(text_file_path, 'r') as file:
    text_content = file.read()

files = {'text': (text_file_path, text_content)}

response = requests.post(url, files=files)

if response.status_code == 200:
    annotated_images_data = response.json()['annotated_images']
    
    for annotated_image in annotated_images_data:
        path = annotated_image['path']
        label = annotated_image['label']
        predictions = annotated_image['predictions']
        print("Annotated image path:", path)
        print("Label:", label)
        print("Predictions:", predictions)

else:
    print("Error:", response.text)
