import mysql.connector
from mysql.connector import Error
from datetime import datetime
import streamlit as st
from utils.config import get_db_config

# Estabelece conexão com o banco de dados
def get_db_connection():
    try:
        config = get_db_config()
        connection = mysql.connector.connect(**config)
        return connection
    except Error as e:
        st.error(f"Erro ao conectar ao banco de dados: {e}")
        return None

# Salva uma nova análise no banco de dados  
def save_scan(user_id, image_path, disease_id, confidence, latitude=None, longitude=None, location_source=None, city_name=None):
    st.write("Iniciando salvamento da análise...")
    st.write(f"Dados recebidos: user_id={user_id}, disease_id={disease_id}, confidence={confidence}")
    
    conn = get_db_connection()
    if not conn:
        st.error("❌ Falha ao conectar ao banco de dados")
        return False
    
    try:
        cursor = conn.cursor()
        query = """
        INSERT INTO scans (user_id, image_path, disease_id, confidence, latitude, longitude, location_source, city_name)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (user_id, image_path, disease_id, confidence, latitude, longitude, location_source, city_name)
        st.write("Executando query com valores:", values)
        
        cursor.execute(query, values)
        conn.commit()
        st.write("✅ Análise salva com sucesso no banco de dados")
        return True
    except Error as e:
        st.error(f"❌ Erro ao salvar análise: {e}")
        st.write("Detalhes do erro:", str(e))
        return False
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
            st.write("Conexão com o banco de dados fechada")

# Obtém todas as análises de um usuário
def get_user_scans(user_id):
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor(dictionary=True)
        query = """
        SELECT s.*, d.name as disease_name, d.scientific_name
        FROM scans s
        JOIN diseases d ON s.disease_id = d.id
        WHERE s.user_id = %s
        ORDER BY s.created_at DESC
        """
        cursor.execute(query, (user_id,))
        return cursor.fetchall()
    except Error as e:
        st.error(f"Erro ao buscar análises: {e}")
        return []
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# Obtém uma doença pelo nome
def get_disease_by_name(name):    
    st.write(f"Buscando doença pelo nome: {name}")
    conn = get_db_connection()
    if not conn:
        st.error("❌ Falha ao conectar ao banco de dados")
        return None
    
    try:
        cursor = conn.cursor(dictionary=True)
        query = """
        SELECT d.*, GROUP_CONCAT(dp.precaution) as precautions
        FROM diseases d
        LEFT JOIN disease_precautions dp ON d.id = dp.disease_id
        WHERE d.name = %s
        GROUP BY d.id
        """
        cursor.execute(query, (name,))
        result = cursor.fetchone()
        
        if result:
            st.write(f"✅ Doença encontrada: ID={result['id']}, Nome={result['name']}")
            if result['precautions']:
                result['precautions'] = result['precautions'].split(',')
            return result
        else:
            st.error(f"❌ Doença não encontrada: {name}")
            return None
    except Error as e:
        st.error(f"❌ Erro ao buscar doença: {e}")
        st.write("Detalhes do erro:", str(e))
        return None
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# Obtém todas as doenças com suas precauções
def get_all_diseases():
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor(dictionary=True)
        query = """
        SELECT d.*, GROUP_CONCAT(dp.precaution) as precautions
        FROM diseases d
        LEFT JOIN disease_precautions dp ON d.id = dp.disease_id
        GROUP BY d.id
        """
        cursor.execute(query)
        diseases = cursor.fetchall()
        for disease in diseases:
            if disease['precautions']:
                disease['precautions'] = disease['precautions'].split(',')
            else:
                disease['precautions'] = []
        return diseases
    except Error as e:
        st.error(f"Erro ao buscar doenças: {e}")
        return []
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# Obtém estatísticas das análises
def get_scan_statistics():
    conn = get_db_connection()
    if not conn:
        return {}
    
    try:
        cursor = conn.cursor(dictionary=True)
        stats = {}
        
        # Total de análises
        cursor.execute("SELECT COUNT(*) as total FROM scans")
        stats['total_scans'] = cursor.fetchone()['total']
        
        # Análises por doença
        cursor.execute("""
            SELECT d.name, COUNT(*) as count
            FROM scans s
            JOIN diseases d ON s.disease_id = d.id
            GROUP BY d.id
        """)
        stats['disease_counts'] = cursor.fetchall()
        
        # Análises por região
        cursor.execute("""
            SELECT city_name, COUNT(*) as count
            FROM scans
            WHERE city_name IS NOT NULL
            GROUP BY city_name
        """)
        stats['region_counts'] = cursor.fetchall()
        
        return stats
    except Error as e:
        st.error(f"Erro ao buscar estatísticas: {e}")
        return {}
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close() 