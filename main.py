import streamlit as st
import sqlite3 as sq
import pandas as pd
from hashlib import sha256


conn = sq.connect('Banco_de_dados.db', check_same_thread=False)
cursor = conn.cursor()

    
def verify_user(user, password):
    user = sha256(user.encode('utf-8')).hexdigest()
    password = sha256(password.encode('utf-8')).hexdigest()
    cursor.execute('select * from professores where nome == ?', (user,))
    professores = cursor.fetchone()
    if professores:
        if user in professores[1] and password in professores[2]:
            return 'professor'
    cursor.execute('select * from alunos where nome == ?', (user,))
    alunos = cursor.fetchone()
    if alunos:
        if user in alunos[1] and password in alunos[3]:
            return 'aluno'
    return None
    
    # Exibindo conteúdo com base na seleção
    
        
@st.dialog('Criaçao de usuario')
def create_user():
    st.title('Criar cadastro')
    nome = st.text_input('Insira o nome do aluno')
    nome = sha256(nome.encode('utf-8')).hexdigest()
    cpf = st.text_input('cpf o nome do aluno')
    cpf = sha256(cpf.encode('utf-8')).hexdigest()
    senha = st.text_input('Insira a senha do aluno')
    senha = sha256(senha.encode('utf-8')).hexdigest()
    if st.button('confirmar'):
        cursor.execute('INSERT INTO alunos (nome, cpf, senha) VALUES (?, ?, ?)', (nome, cpf, senha))
        conn.commit()
        
@st.dialog('Remover Usuario')
def remove_user():
    cpf = st.text_input('cpf do usuario')
    cpf = sha256(cpf.encode('utf-8')).hexdigest()
    if st.button('confirmar'):
        cursor.execute('Delete FROM alunos WHERE cpf == ?', (cpf,))
        conn.commit()
        
              
    
# Função para o conteúdo do menu de Administrador
def exibir_menu_login():
    with st.form(key='login-form'):
        st.title("Menu de login")
        st.text('Seja bem vindo')
        usuarioadm = st.text_input("Usuario")
        senhaadm = st.text_input("Senha")
        if st.form_submit_button("Confirmar"):
            request = verify_user(usuarioadm, senhaadm)
            if request is None:
                st.warning('Usuario ou senha incorretos')
            elif request == 'professor':
                st.session_state.role = 'professor'
                st.rerun()
            elif request == 'aluno':
                st.session_state.role = 'aluno'
                st.rerun()
            else: 
                raise Exception('Erro interno na linha 67')
                
                
def menu_alunos():
    st.title('Seja bem vindo ao menu de alunos')
    # Aqui você pode adicionar mais funcionalidades conforme necessário.

# Função para o conteúdo do menu de Usuário
def exibir_menu_professor():
    st.title("Seja bem vindo")
    st.subheader('Remover alunos')
    removebutton = st.button('confirmar', key='removebutton')
    if removebutton:
        remove_user()
    st.subheader('Cadastrar alunos')
    registerbutton = st.button('Confirmar', key='registerbutton')
    if registerbutton:
        create_user()
    st.subheader('Sair')
    exitbutton = st.button('confirmar', key='exitbutton')
    if exitbutton:
        st.session_state.clear()
        st.rerun()
    # Aqui você pode adicionar mais funcionalidades conforme necessário.

def main():
    # Título do app
    if 'role' not in st.session_state:
        #st.session_state.role = 'indefinido'
        exibir_menu_login()
    elif st.session_state.role == 'professor':
        exibir_menu_professor()
    elif st.session_state.role == 'aluno':
        menu_alunos()


# Execução do aplicativo
if __name__ == "__main__":
    main()
