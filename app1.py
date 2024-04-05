from flask import Flask, request, jsonify
import os
from ultralytics import YOLO
import binascii
import serial


ser = serial.Serial("\\\\.\\COM18", 9600)
if not ser.isOpen():
    ser.open()
    user_reloader= False
print('COM Port 18 open', ser.isOpen())

print(ser)
app = Flask(__name__)

model = YOLO("model_files/best.pt")

def hex_to_img(input_file):
    with open(input_file, "r") as f:
        hex_codes = f.readlines()

    output_image_paths = []
    for i, hex_code in enumerate(hex_codes):
        hex_code = hex_code.strip()
        binary_data = binascii.a2b_hex(bytes(hex_code, "ascii"))
        output_image_path = os.path.join('output_images', f'converted_image_{i}.jpg')
        with open(output_image_path, 'wb') as nf:
            nf.write(binary_data)
        output_image_paths.append(output_image_path)
    
    return output_image_paths

@app.route('/detect_potholes', methods=['POST'])
def detect_potholes():
    if 'image' in request.files:
        image_file = request.files['image']
        temp_image_path = 'output_images/temp_image.jpg'
        image_file.save(temp_image_path)
        results = model(temp_image_path)
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
        print(jsonify({'annotated_images': annotated_image_data}))
        return jsonify({'annotated_images': annotated_image_data})
    elif 'text' in request.files:
        text_file = request.files['text']
        temp_text_path = 'temp_text.txt'
        text_file.save(temp_text_path)
        output_image_paths = hex_to_img(temp_text_path)
        annotated_image_data = []
        for img_path in output_image_paths:
            results = model(img_path)
            output_dir = 'output_images'
            os.makedirs(output_dir, exist_ok=True)
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
    else:
        return jsonify({'error': 'Invalid request. Must contain either an image file or a text file.'}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', use_reloader=False, port=5000, debug=True)
    
