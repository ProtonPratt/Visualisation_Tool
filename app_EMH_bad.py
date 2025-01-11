from flask import Flask, render_template, redirect, url_for, send_file, request, jsonify
import json
import cv2
import numpy as np
import io
import csv
import os

app = Flask(__name__)

filename = '/ssd_scratch/pratyush/visualisation_tool/data/converted_mythic_society_wikimedia.json'
filename_meta = '/ssd_scratch/pratyush/visualisation_tool/data/wikimedia_images_metadata.json'
filename_place = '/ssd_scratch/pratyush/visualisation_tool/data/wikimedia_place_metadata.json'
difficulty_file = '/ssd_scratch/pratyush/visualisation_tool/data/diffuculty_lists/difficultly_Inscription_WikiMedia.json'

# Global Variables
image_data = None
image_lang = {}
languages = []
meta_data = {}
place_meta = {}
global_lang_data = []
difficulty_data = {
    'easy': set(),
    'medium': set(),
    'hard': set()
}

if os.path.exists(difficulty_file):
    if os.stat(difficulty_file).st_size > 0:
        with open(difficulty_file, 'r') as f:
            loaded_data = json.load(f)
            difficulty_data = {k: set(v) for k, v in loaded_data.items()}
        print('Difficulty file found')

with open(filename) as f:
    image_data = json.load(f)
    image_data = image_data['0']

with open(filename_meta) as f:
    meta_data = json.load(f)
    
with open(filename_place) as f:
    place_meta = json.load(f)
    
def extract_langdata():
    # Extract language data from JSON
    global image_lang
    global languages
    
    lang_consort = 'static/lang_dicts/consortium_langWiseTextBook.json'
    lang_newdata = 'static/lang_dicts/newdataset_language.csv'

    # load the consortium data
    with open(lang_consort) as f:
        consortium_data = json.load(f)

    # load the new data which is csv
    with open(lang_newdata) as f:
        reader = csv.reader(f)
        new_data = {}
        for row in reader:
            new_data[row[0]] = row[1]
        
    # combine both the data into image_lang
    image_lang = consortium_data | new_data
    
    # Get all the languages
    languages = list(set([i.lower() for i in image_lang.values()]))

extract_langdata()
# print(image_lang)

image_names = [d[3] for d in image_data]

sorted_images = image_data

# Load image and bounding box data from JSON
def get_image_data():
    return image_data

def get_sorted_images():
    return sorted_images

def get_0_image_data():
    return [[0, 0, 0, 'No Image', [], []]]

def get_image_lang(image_name):
    lang_id = image_name.split('_')[0]
    lang = image_lang.get(lang_id, 'Unknown')
    return lang

def get_sorted_LANG_images(language):
    if language.lower() == 'all':
        return sorted_images
    
    lang_image_list = []
    
    for image in sorted_images:
        image_name = image[3]
        lang_id = image_name.split('_')[0]
        lang = image_lang.get(lang_id, 'Unknown')
        if lang.lower() == language:
            lang_image_list.append(image)
            
    return lang_image_list

# Sorting functionality based on selected metric
def sort_images(metric, reverse=True):
    if metric == 'recall':
        sorted_images = sorted(image_data, key=lambda x: x[0], reverse=reverse)  # Sort by recall
    elif metric == 'precision':
        sorted_images = sorted(image_data, key=lambda x: x[1], reverse=reverse)  # Sort by precision
    elif metric == 'miou':
        sorted_images = sorted(image_data, key=lambda x: x[2], reverse=reverse)  # Sort by mIoU
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

@app.route('/view_json')
def view_json():
    # Get the filename from the query parameter
    filename = request.args.get('filename', None)
    threshold = request.args.get('threshold', 0.6)
    
    if filename is None:
        return "Error: No filename provided", 400
    
    # Full path to the selected JSON file
    json_path = os.path.join('data', filename)
    print(threshold)
    # Load the JSON data
    if os.path.exists(json_path):
        with open(json_path) as f:
            global image_data
            global sorted_images
            image_data = json.load(f)
            image_data = image_data[threshold]
            sorted_images = image_data
    else:
        return "Error: File not found", 404
    
    # Redirect to the first image after loading the new data
    return redirect(url_for('index'))

@app.route('/image/<int:index>')
def view_image(index):
    global sorted_images
    global image_lang
    global global_lang_data
    
    # Get the sorting parameters from the request
    metric = request.args.get('metric', 'none')
    order = request.args.get('order', 'desc') 
    selected_lang = request.args.get('lang', 'all')
        
    if order == 'asc':
        reverse = False
    else:
        reverse = True
    
    sorted_images = sort_images(metric, reverse)
    
    # image_names = [d[3] for d in sorted_images]
    
    if selected_lang.lower() != 'all':
        images = get_sorted_LANG_images(selected_lang)
        global_lang_data = images
    else:
        images = sorted_images
        
    image_names = [d[3] for d in images]
    
    total_images = len(images)
    
    if total_images == 0:
        images = get_0_image_data()
        total_images = 1
    
    if index < 0:
        index = total_images - 1
    elif index >= total_images:
        index = 0

    image_data = images[index]
    recall = image_data[0]
    precision = image_data[1]
    miou = image_data[2]
    image_name = image_data[3]
    image_language = image_lang.get(image_name.split('_')[0], 'Unknown')
    bounding_boxes = image_data[4]
    ground_truth = image_data[5]
    
    img_date = meta_data.get(image_name, 'Unknown')
    img_place = place_meta.get(image_name, 'Unknown')

    prev_index = (index - 1) % total_images
    next_index = (index + 1) % total_images

    view_mode = request.args.get('mode', 'original')
    
    # print(image_name)
    # Difficulty information
    image_difficulties = {
        'easy': image_name in difficulty_data['easy'],
        'medium': image_name in difficulty_data['medium'],
        'hard': image_name in difficulty_data['hard']
    }
    
    print(index, metric, view_mode, order, image_name, image_language, selected_lang)
    # print(image_names)

    return render_template('image_viewer.html',
                           recall=img_date,
                           precision=img_place,
                           miou=miou,
                           image_name=image_name,
                           ground_truth=ground_truth,
                           image_language=image_language,
                           image_names=image_names,
                           available_languages=languages,
                           index=index,
                           total_images=total_images,
                           view_mode=view_mode,
                           language=selected_lang,
                           bounding_boxes=bounding_boxes,
                           prev_index=prev_index,
                           metric=metric,
                           order=order,
                           image_difficulties=image_difficulties,
                           next_index=next_index)

@app.route('/get_processed_image/<int:index>/<string:mode>')
def get_processed_image(index, mode):
    # images = get_image_data()
    global sorted_images
    global global_lang_data
    
    selected_lang = request.args.get('lang', 'all')
    
    if selected_lang.lower() != 'all':
        images = global_lang_data
    else:
        images = sorted_images
    
    # images = sorted_images
    
    image_data = images[index]
    
    image_name = image_data[3]
    bounding_boxes = image_data[4]
    ground_truth = image_data[5] 

    if mode == 'original':
        image_path = os.path.join('/ssd_scratch/pratyush/mythic_society_images_selenium', image_name)
        processed_image = process_image(image_path)
    elif mode == 'predicted':
        image_path = os.path.join('/ssd_scratch/pratyush/mythic_society_images_selenium', image_name)
        processed_image = process_image_with_boxes(image_path, bounding_boxes)
    elif mode == 'gt':
        image_path = os.path.join('/ssd_scratch/pratyush/mythic_society_images_selenium', image_name)
        processed_image = process_image_with_boxes(image_path,[], ground_truth)
    elif mode == 'both':
        image_path = os.path.join('/ssd_scratch/pratyush/mythic_society_images_selenium', image_name)
        processed_image = process_image_with_boxes(image_path, bounding_boxes, ground_truth)
    else:
        raise ValueError('Invalid mode')
    
    print(image_name, index, selected_lang, mode)

    return send_file(
        io.BytesIO(processed_image),
        mimetype='image/tif',
        as_attachment=False
    )
    
def save_difficulty_data():
    # Convert sets to lists for JSON serialization
    data_to_save = {k: list(v) for k, v in difficulty_data.items()}
    with open(difficulty_file, 'w') as f:
        json.dump(data_to_save, f)
        
@app.route('/update_difficulty', methods=['POST'])
def update_difficulty():
    data = request.json
    image_name = data['image_name']
    difficulty = data['difficulty']
    is_checked = data['is_checked']
    
    # Remove image from all difficulty lists first
    for level in difficulty_data:
        difficulty_data[level].discard(image_name)
    
    # Add to selected difficulty if checked
    if is_checked:
        difficulty_data[difficulty].add(image_name)
    
    # Save to file
    save_difficulty_data()
    
    return jsonify({'message': f'Image marked as {difficulty}'})


if __name__ == '__main__':
    app.run(debug=True, port=5001, host='0.0.0.0')
