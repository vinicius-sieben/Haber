import streamlit_authenticator as stauth
import mysql.connector
from mysql.connector import Error
from config import DB_CONFIG

def create_test_user():
    # Dados do usuário
    username = 'teste'
    name = 'Usuário Teste'
    email = 'teste@email.com'
    password = 'teste123'
    
    # Gera o hash da senha
    hashed_password = stauth.Hasher([password]).generate()[0]
    
    try:
        # Conecta ao banco
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Insere o usuário
        cursor.execute(
            "INSERT INTO users (username, name, email, password) VALUES (%s, %s, %s, %s)",
            (username, name, email, hashed_password)
        )
        conn.commit()
        print("Usuário criado com sucesso!")
        print(f"Username: {username}")
        print(f"Senha: {password}")
        
    except Error as e:
        print(f"Erro ao criar usuário: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    create_test_user() 