import streamlit as st
from PIL import Image
import tensorflow as tf
import numpy as np

# Cache para evitar recarregamento do modelo toda hora
@st.cache_resource
def load_tflite_model():
    interpreter = tf.lite.Interpreter(model_path="modelo_soja.tflite")
    interpreter.allocate_tensors()
    return interpreter

# Carregar modelo
interpreter = load_tflite_model()

# Detalhes do modelo
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# Função de pré-processamento
def preprocess_image(image):
    image = image.resize((224, 224))  # Ajuste conforme o seu modelo
    image_array = np.array(image) / 255.0  # Normaliza
    image_array = np.expand_dims(image_array, axis=0).astype(np.float32)
    return image_array

# Interface Streamlit
st.title('🪲 Identificação de Pragas em Folhas de Soja')

uploaded_file = st.file_uploader("📷 Envie uma imagem de folha de soja", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Imagem carregada", use_column_width=True)

    # Pré-processa a imagem
    image_array = preprocess_image(image)

    # Alimenta o modelo
    interpreter.set_tensor(input_details[0]['index'], image_array)
    interpreter.invoke()

    # Obtém o resultado
    prediction = interpreter.get_tensor(output_details[0]['index'])

    # Classes (ajuste com as reais do seu modelo)
    class_names = ['Praga 1', 'Praga 2', 'Praga 3', 'Sem Praga']
    predicted_class = class_names[np.argmax(prediction)]
    confidence = np.max(prediction)

    st.markdown(f"### 🧠 Predição: **{predicted_class}**")
    st.write(f"Confiabilidade: {confidence * 100:.2f}%")
