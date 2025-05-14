import streamlit as st
from PIL import Image, ExifTags
import numpy as np
from utils.doencas import get_doencas, exibir_doenca
import importlib
from streamlit_option_menu import option_menu

st.set_page_config(
    page_title="Haber",
    page_icon="images/haber.png"
)

# Usuários e senhas fixos em dicionário simples
USERS = {
    "joao": "123456",
    "maria": "senha123"
}

def login():
    st.image("images/haber_logo.png")
    st.title("Login")
    username = st.text_input("Usuário")
    password = st.text_input("Senha", type="password")
    login_btn = st.button("Entrar")
    st.write("Usuario: joao ")
    st.write("Senha: 123456")

    if login_btn:
        if username in USERS and USERS[username] == password:
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
        else:
            st.error("Usuário ou senha incorretos")

def logout():
    if st.sidebar.button("Logout"):
        st.session_state["logged_in"] = False
        st.experimental_rerun()

def preprocess_image(image):
    image = image.resize((224, 224))
    image_array = np.array(image) / 255.0
    image_array = np.expand_dims(image_array, axis=0).astype(np.float32)
    return image_array

def display_exif_data(image):
    try:
        exif_data = image._getexif()
        if exif_data is not None:
            for tag, value in exif_data.items():
                tag_name = ExifTags.TAGS.get(tag, tag)
                st.write(f"{tag_name}: {value}")
            return exif_data
        else:
            st.write("Nenhum metadado EXIF encontrado.")
            return None
    except Exception as e:
        st.error(f"Erro ao obter os metadados EXIF: {e}")
        return None

def get_location_from_exif(exif_data):
    try:
        if exif_data:
            gps_info = None
            for tag, value in exif_data.items():
                if ExifTags.TAGS.get(tag) == 'GPSInfo':
                    gps_info = value
                    break

            if gps_info is not None:
                lat_deg = gps_info[2][0]
                lat_min = gps_info[2][1]
                lat_sec = gps_info[2][2]
                lon_deg = gps_info[4][0]
                lon_min = gps_info[4][1]
                lon_sec = gps_info[4][2]

                lat = convert_to_decimal(lat_deg, lat_min, lat_sec)
                lon = convert_to_decimal(lon_deg, lon_min, lon_sec)

                return lat, lon
        return None, None
    except Exception as e:
        st.error(f"Erro ao extrair localização: {e}")
        return None, None

def convert_to_decimal(degrees, minutes, seconds):
    try:
        return degrees + (minutes / 60.0) + (seconds / 3600.0)
    except Exception as e:
        st.error(f"Erro ao converter coordenadas GPS: {e}")
        return None

def main_app():
    st.sidebar.image("images/haber_logo.png", width=200)

    logout()

    with st.sidebar:
        selected = option_menu(
            '',
            ["Home", 'Doenças', 'Modelo', 'Histórico'],
            icons=['house', 'search', 'info-circle', 'collection'],
            default_index=0,
            menu_icon="cast",
            styles={
                "container": {"background-color": "#2D2D2D"},
                "icon": {"color": "white", "font-size": "20px"},
                "nav-link": {"color": "white", "font-weight": "bold"},
                "nav-link-selected": {"background-color": "green", "color": "white"}
            }
        )

    if selected == "Doenças":
        doenças_module = importlib.import_module('paginas.doencas')
        doenças_module.display_content()
    elif selected == "Modelo":
        modelo_module = importlib.import_module('paginas.modelo')
        modelo_module.display_content()
    elif selected == "Histórico":
        modelo_module = importlib.import_module('paginas.historico')
        modelo_module.display_content()
    elif selected == "Home":
        st.title('🪲 Identificação de Pragas em Folhas de Soja')

        uploaded_file = st.file_uploader("📷 Envie uma imagem de folha de soja", type=["jpg", "jpeg", "png"])

        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption="Imagem carregada", use_column_width=True)

            exif_data = display_exif_data(image)
            lat, lon = get_location_from_exif(exif_data)
            if lat and lon:
                st.markdown(f"### 🌍 Localização GPS: Latitude {lat}, Longitude {lon}")
            else:
                st.markdown("### 🌍 Não foi possível obter a localização GPS.")

            image_array = preprocess_image(image)

            class_names = [
                'Mossaic Virus',
                'Southern Blight',
                'Sudden Death Syndrome',
                'Yellow Mosaic',
                'Bacterial Blight',
                'Brown Spot',
                'Crestamento',
                'Ferrugem',
                'Powdery Mildew',
                'Septoria'
            ]

            predicted_class = class_names[0]  # Placeholder fixo
            confidence = 0.95

            st.markdown(f"### 🧠 Predição: **{predicted_class}**")
            st.write(f"Confiabilidade: {confidence * 100:.2f}%")

            doencas = get_doencas()
            if predicted_class in doencas:
                st.markdown("## 📖 Detalhes sobre a doença detectada:")
                exibir_doenca(predicted_class, doencas[predicted_class])
            else:
                st.info("Nenhuma informação detalhada disponível para essa doença.")

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if st.session_state["logged_in"]:
    main_app()
else:
    login()
