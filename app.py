from flask import Flask, request, jsonify, send_from_directory
import boto3
import os
from flask_cors import CORS
from kubernetes import client, config

app = Flask(__name__, static_folder="static")
CORS(app)  # Permitir CORS para o frontend

# Carregar configuração dentro do cluster
config.load_incluster_config()

# Função para obter a URL da rota pública do NooBaa S3
def get_s3_public_endpoint():
    v1 = client.CustomObjectsApi()
    # Pegando o nome do namespace do NooBaa (normalmente 'openshift-storage')
    namespace = "openshift-storage"
    route_name = "s3"
    
    # Consultando a rota para pegar o host
    route = v1.get_namespaced_custom_object(
        group="route.openshift.io", version="v1", namespace=namespace,
        plural="routes", name=route_name
    )
    
    host = route['status']['ingress'][0]['host']
    return f"https://{host}"

# Pegando a URL pública do S3
s3_endpoint_url = get_s3_public_endpoint()

# Credenciais do bucket S3 (usando a Secret do OBC)
s3_access_key = os.getenv('S3_ACCESS_KEY')
s3_secret_key = os.getenv('S3_SECRET_KEY')
bucket_name = os.getenv('S3_BUCKET_NAME')

# Cliente Boto3 S3 configurado para o storage compatível
s3_client = boto3.client(
    's3',
    endpoint_url="https://s3-openshift-storage.apps.nshift02.nobre.labz",  # Use a rota pública
    aws_access_key_id=os.getenv('S3_ACCESS_KEY'),
    aws_secret_access_key=os.getenv('S3_SECRET_KEY'),
    verify=False  # Desativar verificação de SSL
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
    files = [
        {
            'name': obj['Key'],
            'url': s3_client.generate_presigned_url('get_object', Params={'Bucket': bucket_name, 'Key': obj['Key']}, ExpiresIn=3600)
        }
        for obj in response.get('Contents', [])
    ]
    return jsonify(files), 200

@app.route('/delete/<filename>', methods=['DELETE'])
def delete_file(filename):
    s3_client.delete_object(Bucket=bucket_name, Key=filename)
    return 'File deleted successfully', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
