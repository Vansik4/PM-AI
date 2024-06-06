import streamlit as st
import openai
import json
import requests

# Set up the page configuration
st.set_page_config(layout="wide")

# Title of the application
col1, col2 = st.columns([1, 3])
with col1:
    st.image("https://media.licdn.com/dms/image/D4E0BAQFhl8GfNZYDxA/company-logo_200_200/0/1706815368525/ofi_services_logo?e=2147483647&v=beta&t=FR0iH1wUKQ3lCpMo0iV0typjRqasEJHovu17g0Mi8bE", caption="Project Management")

with col2:
    st.title("Project Management Assistant")

# Inicializar el cliente de OpenAI

openai.api_key = st.secrets["OPENAI_API_KEY"]

# Cargar la configuración del modelo
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-4o"

# Inicializar los mensajes de la conversación
if "messages" not in st.session_state:
    st.session_state.messages = []

# Función para cargar el JSON de gestión de proyectos desde GitHub
@st.cache_data
def load_project_management_info(url):
    response = requests.get(url)
    
    if response.status_code != 200:
        st.error(f"Error al obtener el JSON: {response.status_code}")
        st.stop()

    try:
        return response.json()
    except json.JSONDecodeError as e:
        st.error(f"Error al decodificar JSON: {e.msg}")
        st.stop()

# URL del archivo JSON en GitHub
json_url = "https://raw.githubusercontent.com/Vansik4/PM-AI/main/risk.json"

# Cargar la información del proyecto
project_info = load_project_management_info(json_url)

# Convertir el JSON en una cadena de texto
project_info_text = json.dumps(project_info, indent=2)

# Crear un prompt inicial personalizado
initial_prompt = (
    "You are a project management analyst and you will only answer questions about the following:\n"
    f"{project_info_text}\n"
    "Please respond to questions based solely on the information provided."
)

# Show a welcome message and description
if not st.session_state.messages:
    st.session_state.messages.append({"role": "system", "content": initial_prompt})
    with st.chat_message("assistant"):
        st.markdown("I am a virtual assistant specializing in project management. "
                    "You can ask me questions about project management, "
                    "important dates, team members, budget, and more.")

# Display chat history
st.header("Chat History")
for message in st.session_state.messages:
    if message["role"] == "user":
        with st.chat_message("user"):
            st.markdown(message["content"])
    elif message["role"] == "assistant":
        with st.chat_message("assistant"):
            st.markdown(message["content"])

# Handle user input
if prompt := st.chat_input("Ask me a question about project management"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)


    # Llamar a la API de OpenAI para obtener la respuesta
    with st.chat_message("assistant"):
        messages = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
        response = openai.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=messages
        )
        response_text = response.choices[0].message.content
        # Mostrar la respuesta del asistente
        st.markdown(response_text)
    st.session_state.messages.append({"role": "assistant", "content": response_text})

