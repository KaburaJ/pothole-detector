from flask import Flask, request, jsonify
import os
from ultralytics import YOLO
import binascii
import serial

ser = serial.Serial("\\\\.\\COM14", 19200)
if not ser.isOpen():
    ser.open()

app = Flask(__name__)
model = YOLO("model_files/best.pt")

def hex_to_img(hex_code):
    print("Starting")
    start_index = hex_code.find('Start pic') + len('Start pic')
    end_index = hex_code.find('End of pic')
    hex_code = hex_code[start_index:end_index]
    print(hex_code)
    hex_code = hex_code.replace(' ', '').strip()
    binary_data = binascii.a2b_hex(bytes(hex_code, "ascii"))
    print("Conversion Done")
    output_image_path = os.path.join('output_images', 'converted_image.jpg')
    print("Done")
    with open(output_image_path, 'wb') as nf:
        nf.write(binary_data)
    return output_image_path

@app.route('/', methods=['POST'])
def detect_potholes():
    if 'image' in request.files:
        image_file = request.files['image']
        temp_image_path = 'output_images/temp_image.jpg'
        image_file.save(temp_image_path)
        results = model(temp_image_path)
    elif 'hex_code' in request.form:
        hex_code = request.form['hex_code']
        output_image_path = hex_to_img(hex_code)
        results = model(output_image_path)
    else:
        return jsonify({'error': 'Invalid request. Must contain either an image file or a hex code.'}), 400

    output_dir = 'output_images'
    os.makedirs(output_dir, exist_ok=True)
    annotated_image_data = []
    if isinstance(results, list):
        for i, detections in enumerate(results):
            output_image_path = os.path.join(output_dir, f'annotated_image_{i}.jpg')
            detections.save(output_image_path)
            annotated_image_data.append({'path': output_image_path, 'label': 'pothole' if len(detections) > 0 else 'no pothole', 'predictions': detections.names if len(detections) > 0 else []})
    else:
        output_image_path = os.path.join(output_dir, 'annotated_image.jpg')
        results.save(output_image_path)
        annotated_image_data.append({'path': output_image_path, 'label': 'pothole' if len(results) > 0 else 'no pothole', 'predictions': results.names if len(results) > 0 else []})
    
    return jsonify({'annotated_images': annotated_image_data})

if __name__ == '__main__':
    app.run(host='0.0.0.0', use_reloader=False, debug=True)
