import streamlit as st
import sqlite3 as sq
import time as t


conn = sq.connect('Banco_de_dados.db', check_same_thread=False)
cursor = conn.cursor()

    
def verify_user(user, password):
    cursor.execute('select * from professores')
    professores = cursor.fetchall()
    for i in range(len(professores)):
        if user in professores[i][1] and password in professores[i][2]:
            return 'professor'
        else:
            pass
    cursor.execute('select * from alunos')
    alunos = cursor.fetchall()
    password = hash(password)
    for i in range(len(alunos)):
        if user in alunos[i][1] and password in alunos[i][3]:
            return 'aluno'
        else:
            return False
    
    # Exibindo conteúdo com base na seleção
    
        
@st.dialog('dialogo criar usuario')
def create_user():
    st.title('Criar cadastro')
    nome = st.text_input('Insira o nome do aluno')
    cpf = st.text_input('cpf o nome do aluno')
    senha = hash(st.text_input('Insira a senha do aluno'))
    if st.button('confirmar'):
        cursor.execute('INSERT INTO alunos (nome, cpf, senha) VALUES (?, ?, ?)', (nome, cpf, senha))
        conn.commit()
        
        
@st.dialog('dialogo inicial')
def dialog_adm():
    st.subheader("""seja bem vindo""")
    if st.button('Cadastrar aluno'):
        create_user()
    st.button('listar usuarios')
    st.button('remover usuarios')
    
    
# Função para o conteúdo do menu de Administrador
def exibir_menu_login():
    with st.form(key='login-form'):
        st.title("Menu de login")
        usuarioadm = st.text_input("Usuario")
        senhaadm = st.text_input("Senha")
        if st.form_submit_button("""Confirmar"""):
            request = verify_user(usuarioadm, senhaadm)
            if request == 'professor':
                    st.session_state.key = 'professor'
                    st.rerun()
            elif request == 'aluno':
                    st.session_state.key = 'aluno'
                    st.rerun()
                
            else: 
                st.warning('Usuario ou senha incorretos')
                
def menu_alunos():
    st.title('Seja bem vindo ao menu de alunos')
    # Aqui você pode adicionar mais funcionalidades conforme necessário.

# Função para o conteúdo do menu de Usuário
def exibir_menu_professor():
    st.title("Seja bem vindo")
    st.subheader('Listar alunos')
    listbutton = st.button('confirmar', key='list')
    st.subheader('Remover alunos')
    removebutton = st.button('confirmar', key='removebutton')
    st.subheader('Cadastrar alunos')
    registerbutton = st.button('Confirmar', key='registerbutton')
    if registerbutton:
        create_user()
    st.subheader('Sair')
    exitbutton = st.button('confirmar', key='exitbutton')
    if exitbutton:
        st.session_state['key'] = None
        st.rerun()
    # Aqui você pode adicionar mais funcionalidades conforme necessário.

def main():
    # Título do app
    if 'key' not in st.session_state:
        st.session_state.key = 'indefinido'
        exibir_menu_login()

    elif st.session_state.key == 'professor':
        exibir_menu_professor()
        
    elif st.session_state.key == 'aluno':
        menu_alunos()


# Execução do aplicativo
if __name__ == "__main__":
    main()
