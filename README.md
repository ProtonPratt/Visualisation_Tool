# Visualisation_Tool

---

# Image Viewer with Bounding Boxes

This project is a Flask-based web application for viewing images along with predicted and ground truth bounding boxes. The application allows you to navigate through a set of images, display various modes of bounding boxes, zoom in on images, and sort images based on different metrics (recall, precision, mIoU).

## Features

- **View Images**: Navigate through a list of images using "Previous" and "Next" buttons or a dropdown menu.
- **View Modes**: Switch between the following modes:
  - Original: Display the raw image.
  - Predicted: Display the image with predicted bounding boxes.
  - Ground Truth (GT): Display the image with ground truth bounding boxes.
  - Both: Display the image with both predicted and ground truth bounding boxes.
- **Zoom In/Out**: A slider allows zooming in and out on the image. Press and hold the mouse button to drag and move the image within the viewer.
- **Sorting**: Sort images based on recall, precision, or mIoU, and display the sorted results in a sidebar.
- **Overlay Controls**: Bounding boxes can be drawn over the image, and the ground truth boxes can be semi-transparent to better distinguish between predictions and reality.

## Technologies Used

- **Backend**: Flask, OpenCV, NumPy
- **Frontend**: HTML, CSS, JavaScript
- **Image Processing**: OpenCV for reading images and drawing bounding boxes
- **Sorting and Filtering**: JavaScript to handle sorting images by metrics

## Setup and Installation

### Prerequisites

- Python 3.x
- Flask (`pip install flask`)
- OpenCV (`pip install opencv-python`)
- NumPy (`pip install numpy`)

### Getting Started

1. **Clone the repository**:
    ```bash
    git clone https://github.com/your-username/image-viewer-bounding-boxes.git
    cd image-viewer-bounding-boxes
    ```

2. **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3. **Project Structure**:

    - `app.py`: The main Flask application.
    - `static/`: Contains static assets like images, CSS, and JavaScript.
    - `templates/`: Contains the HTML templates for rendering the web pages.
    - `data/images.json`: JSON file containing image paths and bounding box data.
    
    Example of `images.json` structure:
    ```json
    [
        [recall, precision, miou, "image_name.jpg", [[x1, y1, x2, y2], ...], [[gt_x1, gt_y1, gt_x2, gt_y2], ...]],
        ...
    ]
    ```

4. **Run the Application**:
    Run the Flask application on your local machine:
    ```bash
    python app.py
    ```
    By default, the app runs on `http://0.0.0.0:8050`, and is accessible on your local network.
    It can be change to the desired port in the __main__

  1. add the json file path in given structure above replace it in `filename` (line 11)
  2. while opening make sure to call the appropriate threshold (image_data['50']).
  3. Change the image dir in function `get_processed_image` to view the images.
  4. There are 2 kinds of application app.py which runs with gt and app_without_gt it can run without gt but jsons structure is const.

6. **Access the Application**:
    Open your browser and navigate to:
    ```
    http://localhost:8050/
    ```

    Or access it via your local IP address on the network:
    ```
    http://<your-local-ip>:8050/
    ```

### Usage

1. Use the image dropdown to select an image or navigate through images using the "Previous" and "Next" buttons.
2. Choose the view mode from the dropdown (Original, Predicted, GroundTruth, Both).
3. Use the zoom slider to zoom in/out of the image.
4. Press and hold the image to drag and move around the zoomed-in image.
5. Use the "Sort by" dropdown in the sidebar to sort images based on recall, precision, or mIoU.

### Project Example Structure

```
.
├── app.py
├── static
│   ├── css
│   │   └── styles.css
│   ├── images
│   │   └── image1.jpg
│   └── js
│       └── script.js
├── templates
│   └── image_viewer.html
├── data
│   └── images.json
├── requirements.txt
└── README.md
```

### Example JSON Data (`data/images.json`)

```json
[
    [0.8, 0.9, 0.75, "image1.jpg", [[50, 50, 200, 200]], [[45, 45, 195, 195]]],
    [0.7, 0.85, 0.65, "image2.jpg", [[30, 30, 150, 150]], [[35, 35, 145, 145]]]
]
```

### CSS and JS Enhancements

- The sidebar is styled to remain separate from the main content and contains the sorting options.
- The image zoom and drag features are implemented using CSS transitions and JavaScript event listeners.

## Future Enhancements

- Add more sorting options or additional metrics.

### EMH update
- <img width="1273" alt="image" src="https://github.com/user-attachments/assets/64bd01fa-e333-4ecd-b132-8c956244fbbb" />
- The files will be stored in data/difficulty_lists/ (currently in prat ssd nayana)
