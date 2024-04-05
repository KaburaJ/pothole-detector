from flask import Flask, request, jsonify
import os
from PIL import Image
import io
import binascii
from ultralytics import YOLO
import serial
import time

app = Flask(__name__)

model = YOLO("model_files/best.pt")

def hex_to_img(hex_data):
    binary_data = binascii.unhexlify(hex_data)
    image = Image.open(io.BytesIO(binary_data))
    return image

def detect_potholes():
    ser = serial.Serial()
    ser.port = 'COM12'
    ser.baudrate = 19200
    ser.setDTR(False)
    ser.setRTS(False)
    print("Connecting...")

    ser.open()
    ser.write(b'START\n')

    while True:
        if ser.readline().decode().strip() == 'Start pic':
            break

    hex_data = ''
    while True:
        line = ser.readline().decode().strip()
        print(line)
        if line == 'End of pic':
            break
        hex_data += line
        
    print(hex_data)
    ser.close()
    print("Hex data stopped")

    image = hex_to_img(hex_data)
    results = model(image)

    output_dir = 'output_images'
    os.makedirs(output_dir, exist_ok=True)
    if isinstance(results, list):
        annotated_image_data = []
        for i, detections in enumerate(results):
            output_image_path = os.path.join(output_dir, f'annotated_image_{i}.jpg')
            detections.save(output_image_path)
            annotated_image_data.append({'path': output_image_path, 'label': 'pothole' if len(detections) > 0 else 'no pothole', 'predictions': detections.names if len(detections) > 0 else []})
    else:
        output_image_path = os.path.join(output_dir, 'annotated_image.jpg')
        results.save(output_image_path)
        annotated_image_data = [{'path': output_image_path, 'label': 'pothole' if len(results) > 0 else 'no pothole', 'predictions': results.names if len(results) > 0 else []}]

    label = [data['label'] for data in annotated_image_data]
    print("model class result", label)
    
    if label == "pothole": 
       ser.write("1")
    elif label == "no pothole": {
       ser.write("0")
    }
    return annotated_image_data

detect_potholes()

if __name__ == '__main__':
    app.run(host='0.0.0.0', use_reloader=False, port=5000, debug=True)
