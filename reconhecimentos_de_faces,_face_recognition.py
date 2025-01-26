# -*- coding: utf-8 -*-
"""Reconhecimentos de Faces, face_recognition

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1vcCUK8SeviDYLlhnEN8ikCx0M1atmhbw

#Projeto de reconhecimento facial
"""

#configuração de colab para programas base
!pip install --upgrade pip setuptools wheel
!pip install tensorflow-gpu==2.10.0
!pip install tensorflow opencv-python matplotlib
!pip install face_recognition
!pip install dlib==19.24.2

#Importações e Bibliotecas
import cv2
import face_recognition as fr
from google.colab.patches import cv2_imshow
from IPython.display import display, Javascript, Image
from google.colab.output import eval_js
from base64 import b64decode
import numpy as np
import time
import matplotlib.pyplot as plt
import os
import pandas as pd
from google.colab import files
from PIL import Image
import io
import json

# Classe facerec com persistência no banco de dados e DataFrame
class facerec:
    def __init__(self, database_path='database.json', csv_path='face_data.csv'):
        self.database_path = database_path
        self.csv_path = csv_path
        self.database = self.load_database()
        self.df = self.load_dataframe()

    def insert(self, img_input, labels):
        # Verifica se o input é um caminho de arquivo
        if isinstance(img_input, str) and os.path.exists(img_input):
            img = fr.load_image_file(img_input)  # Carregar diretamente do arquivo
        elif isinstance(img_input, bytes):
            img = fr.load_image_file(io.BytesIO(img_input))  # Carregar dos bytes
        else:
            raise ValueError("Entrada inválida. Deve ser um caminho para o arquivo ou dados de imagem em bytes.")

        # Converte imagem para RGB
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encodings = fr.face_encodings(img)

        # Inserir as classificações no banco de dados e DataFrame
        for label, encoding in zip(labels, encodings):
            # Salvar no banco JSON
            if label in self.database:
                self.database[label].append(encoding.tolist())
            else:
                self.database[label] = [encoding.tolist()]

            # Adicionar ao DataFrame usando pd.concat
            new_row = pd.DataFrame({'label': [label], 'encoding': [encoding.tolist()]})
            self.df = pd.concat([self.df, new_row], ignore_index=True)

        # Salvar as alterações
        self.save_database()
        self.save_dataframe()

    def classifier(self, img):
        face_encodings = fr.face_encodings(img)
        labels = ['???' for _ in face_encodings]
        db_encodings = [enc for sublist in self.database.values() for enc in sublist]
        db_labels = [label for label, encodings in self.database.items() for _ in encodings]
        for i, img_enc in enumerate(face_encodings):
            matches = fr.compare_faces(db_encodings, img_enc)
            if any(matches):
                labels[i] = db_labels[matches.index(True)]
        return labels

    def show(self, img_path, clr=True, dim=500):
        img = fr.load_image_file(img_path)
        height, width, _ = img.shape
        ratio = dim / width
        new_height = int(height * ratio)
        img = cv2.resize(img, (dim, new_height))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        if clr:
            face_locations = fr.face_locations(img)
            labels = self.classifier(img)
            for (top, right, bottom, left), label in zip(face_locations, labels):
                cv2.rectangle(img, (left, top), (right, bottom), (0, 255, 0), 2)
                text_width, text_height = cv2.getTextSize(label, cv2.FONT_HERSHEY_DUPLEX, 0.6, 1)[0]
                text_x = left + (right - left) // 2 - text_width // 2
                text_y = bottom + text_height + 5
                cv2.putText(img, label, (text_x, text_y), cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)
            cv2_imshow(img)

    def save_database(self):
        with open(self.database_path, 'w') as f:
            json.dump(self.database, f)

    def load_database(self):
        try:
            with open(self.database_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save_dataframe(self):
        self.df.to_csv(self.csv_path, index=False)

    def load_dataframe(self):
        try:
            return pd.read_csv(self.csv_path)
        except FileNotFoundError:
            # Criar DataFrame vazio se o arquivo não existir
            return pd.DataFrame(columns=['label', 'encoding'])

# Criar uma instância de facerec
fc = facerec()

# Exemplo de inserção manual
fc.insert('/content/p.jpg', ['Pedro Lucas'])

# Confirmar que o banco de dados e o DataFrame foram atualizados
print("\nBanco de dados atualizado:")
for label, encodings in fc.database.items():
    print(f"{label}: {len(encodings)} faces armazenadas.")

print("\nDataFrame atualizado:")
print(fc.df)

"""#2.Reconhecimento através de foto inserida e rotulada:

Ao fazer o upload da imagem, é possível reconhecer a pessoa através da câmera.
"""

# Classe facerec com persistência de banco de dados
class facerec:
    def __init__(self, database_path='database.json'):
        self.database_path = database_path
        self.database = self.load_database()

    def insert(self, img_data, labels):
        img = fr.load_image_file(io.BytesIO(img_data))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encodings = fr.face_encodings(img)
        for label, encoding in zip(labels, encodings):
            if label in self.database:
                self.database[label].append(encoding.tolist())
            else:
                self.database[label] = [encoding.tolist()]
        self.save_database()  # Salvar após cada inserção

    def classifier(self, img):
        face_encodings = fr.face_encodings(img)
        labels = ['???' for _ in face_encodings]
        db_encodings = [enc for sublist in self.database.values() for enc in sublist]
        db_labels = [label for label, encodings in self.database.items() for _ in encodings]
        for i, img_enc in enumerate(face_encodings):
            matches = fr.compare_faces(db_encodings, img_enc)
            if any(matches):
                labels[i] = db_labels[matches.index(True)]
        return labels

    def show(self, img_path, clr=True, dim=500):
        img = fr.load_image_file(img_path)
        height, width, _ = img.shape
        ratio = dim / width
        new_height = int(height * ratio)
        img = cv2.resize(img, (dim, new_height))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        if clr:
            face_locations = fr.face_locations(img)
            labels = self.classifier(img)
            for (top, right, bottom, left), label in zip(face_locations, labels):
                cv2.rectangle(img, (left, top), (right, bottom), (0, 255, 0), 2)
                text_width, text_height = cv2.getTextSize(label, cv2.FONT_HERSHEY_DUPLEX, 0.6, 1)[0]
                text_x = left + (right - left) // 2 - text_width // 2
                text_y = bottom + text_height + 5
                cv2.putText(img, label, (text_x, text_y), cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)
            cv2_imshow(img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

    def save_database(self):
        with open(self.database_path, 'w') as f:
            json.dump(self.database, f)

    def load_database(self):
        try:
            with open(self.database_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

# Função para processar imagens carregadas
def process_uploaded_image(image_data, filename, facerec_instance):
    print(f"Processando a imagem: {filename}")
    # Mostrar a imagem carregada
    image = Image.open(io.BytesIO(image_data))
    image.show()

    # Solicitar o nome do rótulo
    nome = input(f"Digite o nome para a classificação da imagem '{filename}': ")
    facerec_instance.insert(image_data, [nome])
    print(f"A imagem '{filename}' foi rotulada como '{nome}' e adicionada ao banco de dados.")

# Criar uma instância de facerec
fc = facerec()

# Upload de arquivos
uploaded = files.upload()

# Iterar sobre os arquivos carregados e processar cada um
for filename, image_data in uploaded.items():
    process_uploaded_image(image_data, filename, fc)

# Confirmar que o banco de dados foi atualizado
print("\nBanco de dados atualizado:")
for label, encodings in fc.database.items():
    print(f"{label}: {len(encodings)} faces armazenadas.")

# Função para converter a imagem capturada em formato OpenCV
def js_to_image(js_reply):
    image_bytes = b64decode(js_reply.split(',')[1])
    jpg_as_np = np.frombuffer(image_bytes, dtype=np.uint8)
    return cv2.imdecode(jpg_as_np, flags=1)

# JavaScript para abrir a câmera e capturar uma imagem
def take_photo_after_delay():
    js = Javascript('''
        async function takePhotoAfterDelay() {
            const video = document.createElement('video');
            const stream = await navigator.mediaDevices.getUserMedia({video: true});
            video.srcObject = stream;
            await video.play();

//Adicionar o vídeo
            document.body.appendChild(video);
            await new Promise(resolve => setTimeout(resolve, 5000));

//Captura Foto
            const canvas = document.createElement('canvas');
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            canvas.getContext('2d').drawImage(video, 0, 0);

//Para a câmera
            stream.getTracks().forEach(track => track.stop());
            video.remove();

            return canvas.toDataURL('image/jpeg', 0.8);
        }
    ''')
    display(js)
    return eval_js('takePhotoAfterDelay()')

# Inicializa o modelo Haar Cascade
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Captura uma imagem após o delay
try:
    print("A câmera será capturada em 5 segundos. Posicione-se...")
    js_reply = take_photo_after_delay()
    img = js_to_image(js_reply)

    # Converte para escala de cinza
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    # Detecta rostos
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

    # Desenha bounding boxes nos rostos detectados
    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)

    # Salva e exibe a imagem
    filename = 'captured_photo_after_delay.jpg'
    cv2.imwrite(filename, img)
    display(Image(filename))
    print(f"Imagem capturada após 5 segundos e salva como {filename}.")
except Exception as e:
    print(f"Erro: {e}")

# Classifica os rostos na imagem capturada
labels = fc.classifier(img)
print(labels)
# Exibe a imagem com bounding boxes e rótulos
fc.show(filename, clr=True, dim=800)