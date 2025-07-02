"""
    Página del chatbot de la aplicación dashboard de la UNED que permite 
    realizar preguntas al chatbot de huggingface
"""

from groq import Groq
import streamlit as st

client = Groq(api_key= st.secrets.groq_cloud['api_key'])


st.header("Chatbot de consulta", anchor=False)
st.sidebar.subheader("Chatbot de consulta", anchor=False)
# st.sidebar.image("https://cdn-icons-png.flaticon.com/512/4712/4712039.png", width=100)
#st.sidebar.markdown("### 🧠 Chat Memory")
#memory_enabled = st.sidebar.toggle("Enable Chat Memory", value=True)
#if memory_enabled:
#    st.sidebar.markdown("Chat memory is enabled. Your conversation history will be saved.")
#st.sidebar.markdown("Built using **llama-3.3-70b-versatile** via **Groq API**")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


#st.title("💬 AI Assistant")
st.caption("Realiza tu pregunta al asistente de IA")

if st.session_state.chat_history:
    chat_text = "\n\n".join(
        [f"User: {msg['content']}" if msg["role"] == "user" else f"Assistant: {msg['content']}" for msg in st.session_state.chat_history]
    )

    st.download_button(
        label="💾 Download Chat History",
        data=chat_text,
        file_name="chat_history.txt",
        mime="text/plain",
    )


for msg in st.session_state.chat_history:
    if msg["role"] == "user":
        st.markdown(f"<div class='stChatMessage user'>🧑‍💻: {msg['content']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='stChatMessage bot'>🤖: {msg['content']}</div>", unsafe_allow_html=True)

with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_input("Escribe tu mensaje:", key="input", placeholder="Escribe tu mensaje")
    submitted = st.form_submit_button("Enviar pregunta")

if submitted and user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})

 
    #if memory_enabled:
    messages = [{"role": "system", "content": "You are an Ai assistant(LLM)"}]
    messages += st.session_state.chat_history
    messages.append({"role": "user", "content": user_input})
    #else:
    #    messages = [
    #        {"role": "system", "content": "You are an Ai assistant(LLM)"},
    #        {"role": "user", "content": user_input}
    #    ]

    response = client.chat.completions.create(
        messages=messages,
        model="llama-3.3-70b-versatile",
    )

    bot_reply = response.choices[0].message.content

    st.session_state.chat_history.append({"role": "assistant", "content": bot_reply})

    st.rerun()