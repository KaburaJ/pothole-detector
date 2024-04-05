import requests
from PIL import Image

url = 'http://192.168.0.130:5000/detect_potholes'

image_path = 'test_images/pot1.jpg'

image = Image.open(image_path)

files = {'image': open(image_path, 'rb')}

response = requests.post(url, files=files)

if response.status_code == 200:
    annotated_image_paths = response.json()['annotated_images']
    print(annotated_image_paths)
    
    for path in annotated_image_paths:
        annotated_image = Image.open(path)
        annotated_image.show()
else:
    print("Error:", response.text)
