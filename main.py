import streamlit as st
import sqlite3 as sq




conn = sq.connect('Banco_de_dados.db')
cursor = conn.cursor()
    
def verify_user(user, password):
    cursor.execute('select * from Usuarios')
    result = cursor.fetchall()
    if user in result[0][1] and password in result[0][2]:
        return True

def verify_password(self, password):
    if self.password == True:
        return True
    
def main():
    # Título do app
    st.title("Painel Administrador")

    # Barra lateral para navegação
    menu = st.sidebar.selectbox(
        "Escolha um menu",
        ("Administrador", "Usuário")
    )

    # Exibindo conteúdo com base na seleção
    if menu == "Administrador":
        exibir_menu_administrador()
    elif menu == "Usuário":
        exibir_menu_usuario()
        
@st.dialog('dialogo criar usuario')
def create_user():
    st.title('Criar cadastro')
    st.text_input('Insira o nome do aluno')
    
        
@st.dialog('dialogo inicial')
def dialog_adm():
    st.subheader("""seja bem vindo""")
    if st.button('Cadastrar aluno'):
        pass
    st.button('listar usuarios')
    st.button('remover usuarios')
    
    
# Função para o conteúdo do menu de Administrador
def exibir_menu_administrador():
    usuarioadm = st.text_input("Usuario")
    senhaadm = st.text_input("Senha")
    if st.button("""Confirmar
    """):
        request = verify_user(usuarioadm, senhaadm)
        if request == True:
            dialog_adm()
                
    # Aqui você pode adicionar mais funcionalidades conforme necessário.

# Função para o conteúdo do menu de Usuário
def exibir_menu_usuario():
    st.subheader("Bem-vindo ao menu de Usuário")
    st.write("""
        No menu de usuário, você pode:
        - Visualizar seus dados
        - Alterar configurações pessoais
        - Acessar suas funcionalidades
    """)
    # Aqui você pode adicionar mais funcionalidades conforme necessário.

# Execução do aplicativo
if __name__ == "__main__":
    main()
