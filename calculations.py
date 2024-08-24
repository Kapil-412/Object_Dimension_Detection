import cv2
import os
import json
import pandas as pd

# Define the pixel-to-millimeter conversion ratio
pixel_to_mm = 0.26  # Adjust this ratio based on your calibration

def get_annotations(json_file):
    """Extracts image name and bounding box coordinates from the JSON file."""
    with open(json_file, 'r') as file:
        data = json.load(file)
    
    objects = []
    image_name = ""
    for item in data:
        image_name = item['image']
        for annotation in item['annotations']:
            label = annotation['label']
            coords = annotation['coordinates']
            x = coords['x']
            y = coords['y']
            width = coords['width']
            height = coords['height']
            objects.append((label, x, y, width, height))
    
    return image_name, objects

def convert_pixels_to_mm(pixel_values, pixel_to_mm):
    """Converts pixel measurements to millimeters."""
    return [value * pixel_to_mm for value in pixel_values]

def draw_circle_and_process(image_path, annotations, pixel_to_mm):
    """Draws circles on the image and calculates necessary dimensions."""
    image = cv2.imread(image_path)
    
    data = []
    for label, x, y, width, height in annotations:
        # Calculate center, diameter, and radius
        center_x = x + width / 2
        center_y = y + height / 2
        diameter = width
        radius = diameter / 2
        
        # Convert pixel measurements to millimeters
        x_mm, y_mm, width_mm, height_mm = convert_pixels_to_mm([x, y, width, height], pixel_to_mm)
        center_x_mm, center_y_mm, diameter_mm, radius_mm = convert_pixels_to_mm([center_x, center_y, diameter, radius], pixel_to_mm)
        
        # Draw the rectangle and circle on the image
        cv2.rectangle(image, (int(x), int(y)), (int(x + width), int(y + height)), (0, 255, 0), 2)
        cv2.circle(image, (int(center_x), int(center_y)), int(radius), (255, 0, 0), 2)
        
        # Append the calculated data for saving in Excel
        data.append({
            'ImageID': os.path.basename(image_path),
            'Label': label,
            'x_in_mm': round(x_mm, 2),
            'y_in_mm': round(y_mm, 2),
            'width_in_mm': round(width_mm, 2),
            'height_in_mm': round(height_mm, 2),
            'Diameter_in_mm': round(diameter_mm, 2),
            'Radius_in_mm': round(radius_mm, 2),
            'Center_Point': f"({round(center_x_mm, 2)}, {round(center_y_mm, 2)})"
        })
    
    # Save the annotated image in OUTPUT_DB folder
    output_directory = 'OUTPUT_DB'
    os.makedirs(output_directory, exist_ok=True)
    output_image_path = os.path.join(output_directory, os.path.basename(image_path))
    cv2.imwrite(output_image_path, image)
    
    return data

def process_all_images(image_folder, json_folder, pixel_to_mm):
    """Processes all images and their corresponding JSON annotations."""
    all_data = []
    
    for image_file in os.listdir(image_folder):
        if image_file.endswith('.jpg'):
            image_path = os.path.join(image_folder, image_file)
            json_file_path = os.path.join(json_folder, image_file.replace('.jpg', '.json'))
            
            if os.path.exists(json_file_path):
                # Get annotations from JSON
                _, annotations = get_annotations(json_file_path)
                
                # Process the image and extract annotation data
                data = draw_circle_and_process(image_path, annotations, pixel_to_mm)
                
                all_data.extend(data)
            else:
                print(f"Warning: No JSON file found for {image_file}")
    
    return all_data

# Define folders for images and JSON annotations
image_folder = 'DATASET'
json_folder = 'Surface_Area_DB'

# Process all images and collect data
all_data = process_all_images(image_folder, json_folder, pixel_to_mm)

# Save all the data into an Excel file
df = pd.DataFrame(all_data)
excel_file_path = 'new_annotations_data.xlsx'
df.to_excel(excel_file_path, index=False)

print(f"Data has been saved to {excel_file_path}")
