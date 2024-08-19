import os
import requests
from urllib.parse import urlparse
import pandas as pd
import json

# Path to the Excel file
file_path = 'reviews.xlsx'

# Load the Excel file
excel_data = pd.read_excel(file_path, engine='openpyxl')

# Convert data to a list of dictionaries
data_dict = excel_data.to_dict(orient='records')
print(json.dumps(data_dict, indent=2))

# Define the directories to save images and videos
image_save_directory = 'images'
video_save_directory = 'videos'
os.makedirs(image_save_directory, exist_ok=True)
os.makedirs(video_save_directory, exist_ok=True)

# Initialize counters for image and video names
image_counter = 1
video_counter = 1

# Function to download and save files (images and videos)
def download_file(url, save_dir, count, file_type):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check if the request was successful
        # Use the counter to generate a numerical filename
        file_extension = 'jpg' if file_type == 'image' else 'mp4'
        file_name = f'{file_type}_{count}.{file_extension}'
        file_path = os.path.join(save_dir, file_name)
        with open(file_path, 'wb') as file:
            file.write(response.content)
        return file_name
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return None

# Iterate over each item
for item in data_dict:
    # Handle image downloads
    if item['image'] and item['image'] != "[]":
        image_urls = eval(item['image'])  # Convert the image string to a list of URLs
        new_image_names = []
        for url in image_urls:
            image_name = download_file(url, image_save_directory, image_counter, 'image')
            if image_name:
                new_image_names.append(image_name)
                image_counter += 1  # Increment the counter for the next image
        # Update the image field with new local file names
        item['image'] = new_image_names
    
    # Handle video downloads
    if item['video']:
        video_url = item['video']
        video_name = download_file(video_url, video_save_directory, video_counter, 'video')
        if video_name:
            # Update the video field with the new local file name
            item['video'] = video_name
            video_counter += 1  # Increment the counter for the next video

# Print the updated data
print(json.dumps(data_dict, indent=2))

# Convert data_dict to a DataFrame
df = pd.DataFrame(data_dict)

# Save the DataFrame to a CSV file
csv_file_path = 'reviews_updated.csv'
df.to_csv(csv_file_path, index=False)

print(f"Data saved to {csv_file_path}")
