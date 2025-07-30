import os

# Limit CPU usage strictly before importing heavy libraries like numpy, sklearn, etc.
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

import csv
from PIL import Image, ImageFile
from collections import Counter
from sklearn.cluster import KMeans
import numpy as np
from tqdm import tqdm

# Allow loading of truncated images without errors
ImageFile.LOAD_TRUNCATED_IMAGES = True

# 📁 Configuration variables
RAW_SCREENSHOT_DIR = "screenshots_to_optimize"  # Folder with raw screenshots to compress
THUMBNAIL_DIR = "screenshot_thumbnails"         # Folder to save compressed thumbnails
QUALITY = 40                                    # JPEG quality for compression (0-100)
CSV_PATH = 'websites.csv'                       # CSV file with website data

# Create output directory if it doesn't exist
os.makedirs(THUMBNAIL_DIR, exist_ok=True)

# Function to compress a single image once with given quality
def compress_image_once(input_path, output_path, quality=QUALITY):
    with Image.open(input_path) as img:
        # Convert to RGB if image has transparency or palette
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        # Save image as optimized JPEG with specified quality
        img.save(output_path, format='JPEG', optimize=True, quality=quality)

# Compress all images in RAW_SCREENSHOT_DIR and move to THUMBNAIL_DIR
def compress_and_move_images():
    for fname in tqdm(os.listdir(RAW_SCREENSHOT_DIR), desc="Compressing"):
        raw_path = os.path.join(RAW_SCREENSHOT_DIR, fname)
        if not os.path.isfile(raw_path):
            continue  # Skip if not a file (e.g. directories)

        name, _ = os.path.splitext(fname)
        thumb_path = os.path.join(THUMBNAIL_DIR, f"{name}.jpg")
        try:
            compress_image_once(raw_path, thumb_path)
            os.remove(raw_path)  # Remove original raw image after compression
        except Exception as e:
            print(f"Errore su {fname}: {e}")
            continue

# Extract dominant colors from an image using KMeans clustering
def get_dominant_colors(image_path, num_colors=3):
    try:
        image = Image.open(image_path).convert('RGB')
        # Resize to speed up clustering, keeping 150x150 pixels
        image = image.resize((150, 150))
        pixels = np.array(image).reshape(-1, 3)  # Flatten pixel array to (N,3)

        unique_colors = np.unique(pixels, axis=0)
        n_clusters = min(num_colors, len(unique_colors))  # Avoid more clusters than unique colors
        if n_clusters == 0:
            return []

        # Perform KMeans clustering to find dominant colors
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=1)
        kmeans.fit(pixels)

        counts = Counter(kmeans.labels_)  # Count how many pixels belong to each cluster
        centroids = kmeans.cluster_centers_  # RGB values of cluster centers
        # Sort colors by cluster size descending (most dominant first)
        sorted_colors = [centroids[i] for i, _ in counts.most_common(n_clusters)]
        sorted_colors = [tuple(map(int, color)) for color in sorted_colors]

        # If less than requested colors found, pad with empty tuples
        while len(sorted_colors) < num_colors:
            sorted_colors.append(())

        return sorted_colors
    except Exception as e:
        print(f"Error con {image_path}: {e}")
        return []

# Update CSV file in-place by adding dominant colors columns if missing or empty
def update_csv_with_colors(csv_path=CSV_PATH, images_dir=THUMBNAIL_DIR):
    # Load CSV rows into memory
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')
        rows = list(reader)
        fieldnames = reader.fieldnames.copy()

    # Ensure primary, secondary, tertiary columns exist
    for col in ['primary', 'secondary', 'tertiary']:
        if col not in fieldnames:
            fieldnames.append(col)

    # Iterate rows and update color columns if empty
    for row in tqdm(rows, desc="Updating .csv"):
        index = row.get('index')
        if not index:
            continue

        # Skip if all three color fields are already filled
        already_filled = all(row.get(col, "").strip() for col in ['primary', 'secondary', 'tertiary'])
        if already_filled:
            continue

        img_path = os.path.join(images_dir, f"{index}.jpg")
        if os.path.exists(img_path):
            colors = get_dominant_colors(img_path)
            # Convert color tuples to strings, empty string if no color found
            row['primary'] = str(colors[0]) if colors[0] else ''
            row['secondary'] = str(colors[1]) if colors[1] else ''
            row['tertiary'] = str(colors[2]) if colors[2] else ''
        else:
            row['primary'] = row['secondary'] = row['tertiary'] = ''

    # Overwrite CSV with updated rows and new columns
    with open(csv_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=';')
        writer.writeheader()
        writer.writerows(rows)

    print("Done!")

if __name__ == "__main__":
    compress_and_move_images()   # Compress all raw screenshots and move them to thumbnails folder
    update_csv_with_colors()     # Extract dominant colors from thumbnails and update CSV accordingly