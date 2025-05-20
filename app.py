import streamlit as st
from PIL import Image, ExifTags
import numpy as np
from utils.doencas import get_doencas, exibir_doenca
import importlib
from streamlit_option_menu import option_menu
from streamlit_geolocation import streamlit_geolocation
import folium
from folium import plugins
from streamlit_folium import folium_static
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import requests
from utils.auth_config import setup_authenticator
from utils.location import display_location
from utils.image_processing import preprocess_image
from utils.db_operations import save_scan, get_disease_by_name
from utils.auth import get_user_id

st.set_page_config(
    page_title="Haber",
    page_icon="images/haber.png"
)

# Inicializa o authenticator
authenticator = setup_authenticator()

# Tenta fazer login
name, authentication_status, username = authenticator.login('Login', 'main')

if authentication_status == False:
    st.error('Usuário ou senha incorretos')
elif authentication_status == None:
    st.info('Por favor, insira seu usuário e senha')
elif authentication_status:
    st.session_state['username'] = username
    # Usuário está logado
    st.sidebar.image("images/haber_logo.png", width=200)
    
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
        # Botão de logout na sidebar
        authenticator.logout('Logout', 'sidebar')

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
            st.image(image, caption="Imagem carregada", use_container_width=True)

            display_location(image)

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

            # Salva a análise no banco de dados
            user_id = get_user_id()
            if user_id:
                disease = get_disease_by_name(predicted_class)
                if disease:
                    # Obtém a localização
                    location, source = get_location(image)
                    lat, lon = location if location else (None, None)
                    city_name = get_city_from_coords(lat, lon) if lat and lon else None
                    
                    # Salva a análise
                    if save_scan(
                        user_id=user_id,
                        image_path=uploaded_file.name,
                        disease_id=disease['id'],
                        confidence=confidence,
                        latitude=lat,
                        longitude=lon,
                        location_source=source,
                        city_name=city_name
                    ):
                        st.success("✅ Análise salva com sucesso!")
                    else:
                        st.error("❌ Erro ao salvar a análise.")

            doencas = get_doencas()
            if predicted_class in doencas:
                st.markdown("## 📖 Detalhes sobre a doença detectada:")
                exibir_doenca(predicted_class, doencas[predicted_class])
            else:
                st.info("Nenhuma informação detalhada disponível para essa doença.")

def get_gps_coordinates(image):
    try:
        exif_data = image._getexif()
        if exif_data is None:
            return None

        gps_info = {}
        for tag_id, value in exif_data.items():
            tag = ExifTags.TAGS.get(tag_id, tag_id)
            if tag == 'GPSInfo':
                for key, val in value.items():
                    sub_tag = ExifTags.GPSTAGS.get(key, key)
                    gps_info[sub_tag] = val

        if 'GPSLatitude' in gps_info and 'GPSLongitude' in gps_info:
            lat = convert_to_decimal(gps_info['GPSLatitude'], gps_info['GPSLatitudeRef'])
            lon = convert_to_decimal(gps_info['GPSLongitude'], gps_info['GPSLongitudeRef'])
            return lat, lon
        else:
            return None
    except Exception as e:
        st.error(f"Erro ao obter coordenadas GPS: {e}")
        return None

def convert_to_decimal(dms, ref):
    degrees, minutes, seconds = dms
    decimal = degrees + (minutes / 60.0) + (seconds / 3600.0)
    if ref in ['S', 'W']:
        decimal = -decimal
    return decimal

def get_city_from_coords(lat, lon):
    """Função para obter o nome da cidade a partir das coordenadas"""
    try:
        geolocator = Nominatim(user_agent="haber_app")
        location = geolocator.reverse((lat, lon), language='pt')
        if location and location.raw.get('address'):
            address = location.raw['address']
            city = address.get('city') or address.get('town') or address.get('village')
            state = address.get('state')
            if city and state:
                return f"{city}, {state}"
            return "Localização encontrada"
    except (GeocoderTimedOut, Exception) as e:
        return None
    return None

def get_location_from_ip():
    """Função para obter localização baseada no IP"""
    try:
        response = requests.get('https://ipapi.co/json/')
        if response.status_code == 200:
            data = response.json()
            lat = data.get('latitude')
            lon = data.get('longitude')
            if lat and lon:
                return (float(lat), float(lon)), "IP"
    except Exception as e:
        st.error(f"Erro ao obter localização por IP: {str(e)}")
    return None, None

def get_location(image=None):
    """Função que implementa a estratégia de localização em camadas"""
    location = None
    location_source = None
    
    # Variáveis de estado para controle de UI
    if 'location_error' not in st.session_state:
        st.session_state.location_error = None
    if 'show_manual_input' not in st.session_state:
        st.session_state.show_manual_input = False
    if 'retry_count' not in st.session_state:
        st.session_state.retry_count = 0
    if 'using_ip_location' not in st.session_state:
        st.session_state.using_ip_location = False

    st.markdown("""
    ### 📍 Localização Atual
    Para melhor precisão na identificação de doenças em sua região, precisamos da sua localização.
    
    > Isso nos ajuda a:
    > - Mapear a ocorrência de doenças em diferentes regiões
    > - Fornecer recomendações mais precisas
    > - Alertar sobre surtos na sua área
    """)

    # Tentativa 1: Dados EXIF
    if image is not None:
        coordinates = get_gps_coordinates(image)
        if coordinates:
            location = coordinates
            location_source = "EXIF"
            st.success("✅ Localização detectada automaticamente a partir da imagem!")
            return location, location_source
        else:
            st.info("""
            ℹ️ **Não foi possível detectar a localização automaticamente**
            
            Por favor, escolha uma das opções abaixo para informar sua localização:
            """)

    # Opções de localização
    location_method = st.radio(
        "Escolha como deseja fornecer sua localização:",
        ["Digitar Cidade", "Selecionar no Mapa", "Baseado em IP"],
        help="Escolha o método mais conveniente para você"
    )

    if location_method == "Digitar Cidade":
        city = st.text_input("Digite sua cidade:", placeholder="Ex: Curitiba, PR")
        if city:
            try:
                with st.spinner("Buscando localização..."):
                    geolocator = Nominatim(user_agent="haber_app")
                    location_data = geolocator.geocode(city + ", Brasil")
                    if location_data:
                        location = (location_data.latitude, location_data.longitude)
                        location_source = "Manual (Cidade)"
                        return location, location_source
                    else:
                        st.error("Cidade não encontrada. Tente ser mais específico (ex: 'São Paulo, SP')")
            except Exception as e:
                st.error("Erro ao buscar localização. Tente usar o mapa.")

    elif location_method == "Selecionar no Mapa":
        st.markdown("""
        👉 **Como usar o mapa:**
        1. Navegue pelo mapa usando dois dedos para mover e dar zoom
        2. Toque no local desejado para marcar
        3. Ajuste a posição do marcador se necessário
        4. Toque em 'Confirmar Localização'
        """)
        
        # Criando um mapa centralizado no Brasil
        m = folium.Map(
            location=[-15.788497, -47.879873],
            zoom_start=4,
            scrollWheelZoom=True,
            dragging=True
        )
        
        # Adicionando um marcador que pode ser arrastado
        marker = folium.Marker(
            [-15.788497, -47.879873],
            popup="Toque e segure para mover",
            draggable=True
        )
        marker.add_to(m)
        
        # Adicionando controles de zoom mais visíveis para mobile
        folium.plugins.Fullscreen().add_to(m)
        
        # Exibindo o mapa com altura adequada para mobile
        folium_static(m, height=400)
        
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("🔄 Centralizar Mapa", use_container_width=True):
                m.location = [-15.788497, -47.879873]
                m.zoom_start = 4
                st.rerun()
        with col2:
            if st.button("✅ Confirmar Localização", use_container_width=True):
                location = (marker.location[0], marker.location[1])
                location_source = "Manual (Mapa)"
                return location, location_source

    elif location_method == "Baseado em IP":
        with st.spinner("Obtendo localização baseada em IP..."):
            location, location_source = get_location_from_ip()
            if location:
                return location, location_source
            else:
                st.error("Não foi possível obter localização por IP. Tente digitar sua cidade.")

    return None, None

def display_location(image=None):
    """Função para exibir a localização obtida"""
    location, source = get_location(image)
    if location and None not in location:
        lat, lon = location
        
        # Obtendo nome da cidade
        city_name = get_city_from_coords(lat, lon)
        
        st.markdown(f"### 🌍 Localização ({source})")
        if city_name:
            st.markdown(f"**Local:** {city_name}")
        
        # Show more precise coordinate information
        st.markdown("""
        **Coordenadas precisas:**
        """)
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Latitude:** {lat}")
            st.markdown(f"*Formato decimal:* {lat:.8f}")
        with col2:
            st.markdown(f"**Longitude:** {lon}")
            st.markdown(f"*Formato decimal:* {lon:.8f}")
        
        # Exibindo o mapa com a localização
        m = folium.Map(location=[lat, lon], zoom_start=12)
        folium.Marker([lat, lon]).add_to(m)
        folium_static(m)
    else:
        if not st.session_state.show_manual_input and st.session_state.retry_count > 2:
            st.warning("🔍 Está tendo problemas? Tente a entrada manual de localização.")
