from flask import Flask, request, jsonify
import os
import base64
import tempfile
import json
import requests
from io import BytesIO
from firebase_admin import credentials, firestore, initialize_app
from PIL import Image
from dotenv import load_dotenv
from deepface import DeepFace

# Load configuration from .env file
load_dotenv()

# Initialize the Flask app
app = Flask(__name__)

# Get secret key and Firebase admin key path from environment variables
SECRET_KEY = os.getenv('SECRET_KEY', 'defaultsecretkey')
firebase_admin_key_base64 = os.getenv('FIREBASE_ADMIN_KEY_PATH')
firebase_admin_key_json = base64.b64decode(firebase_admin_key_base64).decode('utf-8')

# Convert to dictionary
firebase_admin_key_dict = json.loads(firebase_admin_key_json)

# Initialize Firebase with the dictionary
cred = credentials.Certificate(firebase_admin_key_dict)
firebase_app = initialize_app(cred)
db = firestore.client()

@app.route("/")
def hello():
    print("Root endpoint hit.")  # Log
    return "Hello, it's Flask"

# Route to test the app
@app.route("/api/test", methods=["GET"])
def test():
    print("Test endpoint hit.")  # Log
    return "Hello, World!"

# Route to match images using DeepFace for face recognition
@app.route("/api/match-images/", methods=["POST"])
def match_images():
    print("match_images endpoint hit.")  # Log

    if 'reference_image' not in request.files:
        print("No reference image found in the request.")  # Log
        return jsonify({"error": "No image part"}), 400

    reference_image = request.files['reference_image']
    group_id = request.form.get("group_id", "uLFXzY5qXGg23xmFoacq")
    print(f"Group ID: {group_id}")  # Log

    # Validate image format
    if reference_image.content_type not in ["image/jpeg", "image/png"]:
        print("Invalid image format.")  # Log
        return jsonify({"error": "Invalid image format. Use JPEG or PNG."}), 400

    # Save the reference image to a temporary file
    try:
        print("Saving reference image to temporary file...")  # Log
        temp_ref_image = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
        reference_image.save(temp_ref_image.name)
        reference_image_path = temp_ref_image.name
        temp_ref_image.close()  # Close the file after saving the image
        print(f"Reference image saved at {reference_image_path}")  # Log
    except Exception as e:
        print(f"Error saving reference image: {str(e)}")  # Log
        return jsonify({"error": f"Failed to save reference image: {str(e)}"}), 500

    # Get image URLs from Firestore using the provided group ID
    try:
        print(f"Fetching image URLs from Firestore for group {group_id}...")  # Log
        image_urls = get_image_urls_from_firestore(group_id)
        print(f"Fetched {len(image_urls)} image URLs.")  # Log
    except Exception as e:
        print(f"Error fetching image URLs: {str(e)}")  # Log
        return jsonify({"error": f"Failed to fetch image URLs: {str(e)}"}), 500

    # Process the images and find matches using DeepFace
    print("Starting image matching process...")  # Log
    matching_images = process_images_from_urls_in_batches(reference_image_path, image_urls)

    # Cleanup the temporary reference image file
    if os.path.exists(reference_image_path):
        os.remove(reference_image_path)
        print(f"Deleted temporary reference image at {reference_image_path}")  # Log

    print(f"Matching images: {matching_images}")  # Log
    return jsonify({"matching_images": matching_images})

# Helper function to get image URLs from Firestore
def get_image_urls_from_firestore(group_id: str):
    print(f"Getting image URLs for group {group_id}...")  # Log
    image_urls = []
    docs = db.collection('groups').document(group_id).collection('photos').stream()

    for doc in docs:
        data = doc.to_dict()
        image_urls.append(data.get('photoURL'))  # Assuming 'photoURL' field contains the image URL
    print(f"Retrieved {len(image_urls)} URLs.")  # Log
    return image_urls

# Face recognition logic to process image URLs in batches using DeepFace
def process_images_from_urls_in_batches(reference_image_path, image_urls, batch_size=5, model_name='VGG-Face', distance_metric='cosine', threshold=0.4):
    print(f"Processing images in batches of {batch_size}...")  # Log
    matching_images = []

    for i in range(0, len(image_urls), batch_size):
        batch_urls = image_urls[i:i + batch_size]
        print(f"Processing batch {i//batch_size + 1}: {batch_urls}")  # Log

        for url in batch_urls:
            try:
                print(f"Fetching image from URL: {url}")  # Log
                # Fetch image from URL
                response = requests.get(url)
                response.raise_for_status()  # Ensure the request was successful

                # Open the fetched image
                img = Image.open(BytesIO(response.content))

                # Ensure image is in RGB format
                if img.mode != 'RGB':
                    img = img.convert('RGB')

                # Save the fetched image to a temporary file
                temp_img = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
                img.save(temp_img.name)
                img_path = temp_img.name
                temp_img.close()

                print(f"Running DeepFace verification for image: {url}")  # Log
                # Use DeepFace to verify if the fetched image matches the reference image
                result = DeepFace.verify(img1_path=reference_image_path, img2_path=img_path, model_name="Facenet")

                # Check if the distance is within the acceptable threshold (matching faces)
                if result['verified']:
                    print(f"Image matched: {url}")  # Log
                    matching_images.append(url)

                # Cleanup the temporary fetched image file
                if os.path.exists(img_path):
                    os.remove(img_path)
                    print(f"Deleted temporary image at {img_path}")  # Log

            except requests.exceptions.RequestException as e:
                print(f"Error fetching image from URL {url}: {str(e)}")  # Log
            except Exception as e:
                print(f"Error processing image {url}: {str(e)}")  # Log

    print("Image processing completed.")  # Log
    return matching_images

# Main entry point for the application
if __name__ == '__main__':
    # Use the PORT environment variable, defaulting to 5000 if not set
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
