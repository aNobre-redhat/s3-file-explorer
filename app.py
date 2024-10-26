from flask import Flask, request, jsonify, send_from_directory
import boto3
import os
from flask_cors import CORS

app = Flask(__name__, static_folder="static")
CORS(app)  # Permitir CORS para o frontend

# Credenciais do bucket S3 (usando a Secret do OBC)
s3_access_key = os.getenv('S3_ACCESS_KEY')
s3_secret_key = os.getenv('S3_SECRET_KEY')
s3_endpoint_url = os.getenv('S3_ENDPOINT_URL')
bucket_name = os.getenv('S3_BUCKET_NAME')

# Cliente Boto3 S3 configurado para o storage compatível
s3_client = boto3.client(
    's3',
    aws_access_key_id=s3_access_key,
    aws_secret_access_key=s3_secret_key,
    endpoint_url=s3_endpoint_url
)

@app.route('/')
def serve_frontend():
    return send_from_directory(app.static_folder, 'frontend.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file provided', 400
    file = request.files['file']
    s3_client.upload_fileobj(file, bucket_name, file.filename)
    return 'File uploaded successfully', 200

@app.route('/list', methods=['GET'])
def list_files():
    response = s3_client.list_objects_v2(Bucket=bucket_name)
    files = [obj['Key'] for obj in response.get('Contents', [])]
    return jsonify(files), 200

@app.route('/delete/<filename>', methods=['DELETE'])
def delete_file(filename):
    s3_client.delete_object(Bucket=bucket_name, Key=filename)
    return 'File deleted successfully', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

@app.before_request
def log_request():
    print(f"Received request: {request.method} {request.path}")
