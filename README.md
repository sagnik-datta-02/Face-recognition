# 🔥 Face Recognition with DeepFace and Firebase Integration

This project is a **Flask-based** web application for performing face recognition using [DeepFace](https://github.com/serengil/deepface) and image data stored in Firebase Firestore. Users can upload a reference image, and the app will match it against images stored in a Firestore collection. 

## Features

- 🌐 **Flask Backend**: Lightweight server for handling image matching requests.
- 🖼️ **DeepFace**: Perform face recognition using pre-trained models like `VGG-Face` and `Facenet`.
- ☁️ **Firebase Firestore**: Retrieve image URLs from Firestore collections based on group IDs.
- 📦 **Dockerized Application**: Ready to deploy using Docker.

## 🏗️ Architecture

- The app takes a reference image as input via a POST request.
- Retrieves image URLs from Firebase Firestore, based on the provided `group_id`.
- Compares the reference image with the fetched images using DeepFace.
- Returns a list of image URLs that match the reference image.

## 🛠️ Installation & Setup

### Prerequisites

Before running the project, ensure you have the following installed:

- Python 3.x
- Docker (if using Docker)
- Firebase admin credentials

### 1. Clone the Repository

```bash
git clone [https://github.com/yourusername/your-repo-name.git](https://github.com/sagnik-datta-02/Face-recognition.git)
cd Face-recognition
```

### 2. Install Dependencies

Create a virtual environment and install the required dependencies:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Setup Firebase Admin SDK

You need to provide Firebase Admin SDK credentials. The credentials are expected to be base64 encoded and stored in a `.env` file. Example:

1. Convert the Firebase Admin SDK JSON file to base64:

```bash
cat firebase-adminsdk.json | base64
```

2. Create a `.env` file and add the following:

```
SECRET_KEY=your_secret_key
FIREBASE_ADMIN_KEY_PATH=base64_encoded_firebase_key
```

### 4. Run the App

```bash
flask run --host=0.0.0.0 --port=5000
```

Your app will be running at `http://localhost:5000`.

## 🔥 Docker Setup

### 1. Build Docker Image

If you haven't built the Docker image yet, you can build it with:

```bash
docker build -t face-recognition-app .
```

### 2. Run with Docker

Run the Docker container:

```bash
docker run -d -p 5000:5000 face-recognition-app
```

The app will be available at `http://localhost:5000`.

### 3. Pull from Docker Hub

You can also pull the pre-built Docker image from Docker Hub:

```bash
docker pull sagnikdatta/flask-back
```

Link to Docker Hub: [Docker Image](https://hub.docker.com/r/sagnikdatta/flask-back)

### 4. Run Docker Image

```bash
docker run -d -p 5000:5000 sagnikdatta/flask-back
```

## 🔍 API Endpoints

### Test Endpoint

```http
GET /api/test
```

Returns: `Hello, World!` — a simple test response to check if the server is running.

### Match Images Endpoint

```http
POST /api/match-images/
```

- **Parameters**:
  - `reference_image` (form-data): JPEG/PNG image to be used as the reference.
  - `group_id` (form-data): Group ID to fetch images from Firestore. Default: `uLFXzY5qXGg23xmFoacq`.

- **Response**:
  - `matching_images`: List of URLs of images that match the reference image.

#### Example cURL

```bash
curl -X POST http://localhost:5000/api/match-images/ \
  -F 'reference_image=@/path/to/your/image.jpg' \
  -F 'group_id=your-group-id'
```

## 🧑‍💻 Contributing

1. Fork the repo
2. Create your feature branch (`git checkout -b feature/my-new-feature`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin feature/my-new-feature`)
5. Create a new Pull Request

## 🛡️ License

This project is licensed under the MIT License.

---



