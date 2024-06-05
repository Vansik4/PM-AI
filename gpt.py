import streamlit as st
from openai import OpenAI
import json

# Título de la aplicación
st.title("Asistente de Gestión de Proyectos")

# Inicializar el cliente de OpenAI
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Función para procesar la respuesta y enriquecerla con información del JSON
def process_response(response, project_info):
    if "riesgo" in response.lower() or "risk" in response.lower():
        for risk in project_info['Risk']:
            response += f"\n\nRiesgo ID {risk['Risk Id']}: {risk['Description']}"
            response += f"\nImpacto: {risk['Impact']}"
            response += f"\nProbabilidad: {risk['Probability']}"
            response += f"\nEstado: {risk['Risk/Stopper Status']}\n"
    if "tarea" in response.lower() or "task" in response.lower():
        for task in project_info['Task']:
            response += f"\n\nTarea ID {task['Task id']}: {task['Task/Activity']}"
            response += f"\nSprint: {task['Sprint']}"
            response += f"\nFecha de inicio: {task['Star Date']}"
            response += f"\nFecha de finalización: {task['Finish Date']}"
            response += f"\nEstado de la tarea: {task['Task Status']}"
            response += f"\nResponsable: {task['Responsible for the task']}\n"
    return response

# Cargar la configuración del modelo
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

# Inicializar los mensajes de la conversación
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostrar mensajes previos en el chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Función para cargar el JSON de gestión de proyectos
@st.cache
def load_project_management_info():
    with open("risk.json", "r") as f:
        return json.load(f)

# Cargar la información del proyecto
project_info = load_project_management_info()

# Mostrar un mensaje de bienvenida y descripción
if not st.session_state.messages:
    welcome_message = ("Soy un asistente virtual especializado en gestión de proyectos. "
                       "Puedes hacerme preguntas sobre el manejo del proyecto, "
                       "fechas importantes, miembros del equipo, presupuesto y más.")
    st.session_state.messages.append({"role": "assistant", "content": welcome_message})
    with st.chat_message("assistant"):
        st.markdown(welcome_message)

# Manejar el input del usuario
if prompt := st.chat_input("Hazme una pregunta sobre la gestión del proyecto"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Llamar a la API de OpenAI para obtener la respuesta
    with st.chat_message("assistant"):
        messages = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
        stream = client.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=messages,
            stream=True,
        )
        response = "".join([chunk["choices"][0]["delta"]["content"] for chunk in stream])
        
        # Enriquecer la respuesta con información del JSON si es necesario
        response = process_response(response, project_info)
        
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})

