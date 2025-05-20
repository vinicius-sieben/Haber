# pages/historico.py

import streamlit as st
import pandas as pd
from utils.db_operations import get_user_scans, get_scan_statistics
from utils.auth import get_user_id

#st.set_page_config(page_title="Doenças da Soja", layout="wide")
def display_content():
    st.title("🦠 Histórico de Análises")
    
    # Obtém o ID do usuário logado
    user_id = get_user_id()
    if not user_id:
        st.error("Usuário não autenticado")
        return
    
    # Obtém as análises do usuário
    scans = get_user_scans(user_id)
    
    if not scans:
        st.info("Nenhuma análise encontrada no histórico.")
        return
    
    # Converte para DataFrame
    df = pd.DataFrame(scans)
    
    # Formata a data
    df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%d/%m/%Y %H:%M')
    
    # Seleciona e renomeia as colunas
    df = df[['created_at', 'disease_name', 'confidence', 'city_name', 'latitude', 'longitude']]
    df.columns = ['Data e Hora', 'Doença', 'Confiabilidade', 'Cidade', 'Latitude', 'Longitude']
    
    # Exibe o DataFrame
    st.dataframe(df, use_container_width=True)
    
    # Exibe estatísticas
    st.subheader("📊 Estatísticas")
    stats = get_scan_statistics()
    
    if stats:
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Total de Análises", stats['total_scans'])
            
            if stats['disease_counts']:
                st.write("Análises por Doença:")
                disease_df = pd.DataFrame(stats['disease_counts'])
                st.bar_chart(disease_df.set_index('name')['count'])
        
        with col2:
            if stats['region_counts']:
                st.write("Análises por Região:")
                region_df = pd.DataFrame(stats['region_counts'])
                st.bar_chart(region_df.set_index('city_name')['count'])
