"""
    Páginadel chatbot de la aplicación dashboard de la UNED que permite 
    realizar preguntas al chatbot de huggingface
"""
import streamlit as st
from hugchat import hugchat
from hugchat.login import Login


st.subheader("Chatbot de consulta")
st.sidebar.subheader("Chatbot de consulta", anchor=False)


# Function for generating LLM response
def generate_response(prompt_input, email, passwd):
    """
    Función para generar la respuesta del chatnot
    Args:
        prompt_input (_type_): prompt introducido por el usuario
        email (_type_): correo del usuario
        passwd (_type_): clave del usuario

    Returns:
        _type_: _description_
    """
    # Hugging Face Login
    sign = Login(email, passwd)
    cookies = sign.login()
    # Create ChatBot
    chatbot = hugchat.ChatBot(cookies=cookies.get_dict())
    return chatbot.chat(prompt_input)

# Hugging Face Credentials
with st.sidebar:
    st.title('🤗💬 HugChat')
    if ('email' in st.secrets.hugchat) and ('pass' in st.secrets.hugchat):
        st.success('HuggingFace Login credentials already provided!', icon='✅')
        hf_email = st.secrets.hugchat['email']
        hf_pass = st.secrets.hugchat['pass']
    else:
        hf_email = st.text_input('Enter E-mail:', type='password')
        hf_pass = st.text_input('Enter password:', type='password')
        if not (hf_email and hf_pass):
            st.warning('Please enter your credentials!', icon='⚠️')
        else:
            st.success('Proceed to entering your prompt message!', icon='👉')

# Store LLM generated responses
if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": "¿Cómo puedo ayudarle?"}]

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# User-provided prompt
if prompt := st.chat_input(disabled=not (hf_email and hf_pass)):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

# Generate a new response if last message is not from assistant
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = generate_response(prompt, hf_email, hf_pass)
            st.write(response)
    message = {"role": "assistant", "content": response}
    st.session_state.messages.append(message)
