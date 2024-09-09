from flask import Flask, render_template, redirect, url_for, send_file, request
import json
import cv2
import numpy as np
import io
import os

app = Flask(__name__)

image_data = None
with open('data/images.json') as f:
    image_data = json.load(f)

image_names = [d[3] for d in image_data]

sorted_images = image_data

# Load image and bounding box data from JSON
def get_image_data():
    return image_data

# Sorting functionality based on selected metric
def sort_images(metric):
    if metric == 'recall':
        sorted_images = sorted(image_data, key=lambda x: x[0], reverse=True)  # Sort by recall
    elif metric == 'precision':
        sorted_images = sorted(image_data, key=lambda x: x[1], reverse=True)  # Sort by precision
    elif metric == 'miou':
        sorted_images = sorted(image_data, key=lambda x: x[2], reverse=True)  # Sort by mIoU
    else:
        sorted_images = image_data  # Default: no sorting   
    
    return sorted_images

def process_image_with_boxes(image_path, bounding_boxes, bounding_boxes_gt=None):
    # Load the image using OpenCV
    image = cv2.imread(image_path)
    # Convert bounding box data and draw them on the image
    for box in bounding_boxes:
        x1, y1, x2, y2 = map(int, box)
        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 0, 255), 1)
    
    overlay = image.copy() 
    if bounding_boxes_gt is not None:
        for box in bounding_boxes_gt:
            x1, y1, x2, y2 = map(int, box)
            cv2.rectangle(image, (x1, y1), (x2, y2), (255, 0, 0), -1)    
        # Create a translucent overlay by blending the original image with the overlay
        alpha = 0.8  # Transparency factor (0.0 to 1.0)
        cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0, image)
    
    _, buffer = cv2.imencode('.jpg', image)
    return buffer.tobytes()

def process_image(image_path):
    image = cv2.imread(image_path)
    _, buffer = cv2.imencode('.jpg', image)
    return buffer.tobytes()

@app.route('/')
def index():
    return redirect(url_for('view_image', index=0, mode='original', metric='none'))

@app.route('/image/<int:index>')
def view_image(index):
    metric = request.args.get('metric', 'none')  # Get sorting metric
    print(metric)
    sorted_images = sort_images(metric)
    
    image_names = [d[3] for d in sorted_images]
    
    # images = get_image_data()
    images = sorted_images
    
    total_images = len(images)
    if index < 0:
        index = total_images - 1
    elif index >= total_images:
        index = 0

    image_data = images[index]
    recall = image_data[0]
    precision = image_data[1]
    miou = image_data[2]
    image_name = image_data[3]
    bounding_boxes = image_data[4]
    ground_truth = image_data[5]

    prev_index = (index - 1) % total_images
    next_index = (index + 1) % total_images

    view_mode = request.args.get('mode', 'original')
    
    print(index, metric, view_mode)
    print(image_names)

    return render_template('image_viewer.html',
                           recall=recall,
                           precision=precision,
                           miou=miou,
                           image_name=image_name,
                           ground_truth=ground_truth,
                           image_names=image_names,
                           index=index,
                           total_images=total_images,
                           view_mode=view_mode,
                           bounding_boxes=bounding_boxes,
                           prev_index=prev_index,
                           metric=metric,
                           next_index=next_index)

@app.route('/get_processed_image/<int:index>/<string:mode>')
def get_processed_image(index, mode):
    # images = get_image_data()
    images = sorted_images
    
    image_data = images[index]
    
    image_name = image_data[3]
    bounding_boxes = image_data[4]
    ground_truth = image_data[5] 

    if mode == 'original':
        image_path = os.path.join('static', 'images', image_name)
        processed_image = process_image(image_path)
    elif mode == 'predicted':
        image_path = os.path.join('static', 'images', image_name)
        processed_image = process_image_with_boxes(image_path, bounding_boxes)
    elif mode == 'gt':
        image_path = os.path.join('static', 'images', image_name)
        processed_image = process_image_with_boxes(image_path,[], ground_truth)
    elif mode == 'both':
        image_path = os.path.join('static', 'images', image_name)
        processed_image = process_image_with_boxes(image_path, bounding_boxes, ground_truth)
    else:
        raise ValueError('Invalid mode')

    return send_file(
        io.BytesIO(processed_image),
        mimetype='image/jpeg',
        as_attachment=False
    )

if __name__ == '__main__':
    app.run(debug=True, port=8050, host='0.0.0.0')
