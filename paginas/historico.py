# pages/historico.py

import streamlit as st
import pandas as pd
import numpy as np

#st.set_page_config(page_title="Doenças da Soja", layout="wide")
def display_content():
    st.title("🦠 Histórico de Pragas")
    st.markdown("Pragas identificadas...")
    df = pd.DataFrame(np.random.randn(10, 5), columns=("Data e Hora", "Praga","Latitude","Longitude","Usuario"))    
    st.dataframe(df)  # Same as st.write(df)
