import streamlit as st
import openai
import json
import requests

# Título de la aplicación
st.title("Asistente de Gestión de Proyectos")

# Inicializar el cliente de OpenAI
api_key = "sk-proj-mHFAcE7C4GBwsxOjgDtdT3BlbkFJlkHiAMj00dZVSreuZR2W"
openai.api_key = api_key

# Función para procesar la respuesta y enriquecerla con información del JSON
def process_response(prompt, response, project_info):
    if "riesgos" in prompt.lower():
        risks = [
            f"Riesgo ID {risk['Risk Id']}: {risk['Description']}, Impacto: {risk['Impact']}, Probabilidad: {risk['Probability']}"
            for risk in project_info['Risk']
        ]
        if risks:
            response = "Riesgos identificados:\n" + "\n".join(risks)
        else:
            response = "No hay riesgos identificados."
    elif "tareas en overdue" in prompt.lower():
        overdue_tasks = [
            f"Tarea ID {task['Task id']}: {task['Task/Activity']}, Responsable: {task['Responsible for the task']}"
            for task in project_info['Task'] if task['Task Status'].lower() == 'overdue'
        ]
        if overdue_tasks:
            response = "Tareas en overdue:\n" + "\n".join(overdue_tasks)
        else:
            response = "No hay tareas en overdue."
    elif "personas involucradas" in prompt.lower() or "nombres de las personas" in prompt.lower():
        people = set(task['Responsible for the task'] for task in project_info['Task'])
        if people:
            response = "Personas involucradas en el proyecto:\n" + "\n".join(people)
        else:
            response = "No se encontraron datos de personas involucradas en el proyecto."
    else:
        response += "\n"
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

@st.cache_data
def load_project_management_info(url):
    response = requests.get(url)
    response.raise_for_status()  # Para manejar errores de HTTP
    return response.json()

# URL del archivo JSON en GitHub
json_url = "https://raw.githubusercontent.com/Vansik4/PM-AI/main/risk.json"

# Cargar la información del proyecto
project_info = load_project_management_info(json_url)

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

    # Recargar la información del proyecto antes de responder
    project_info = load_project_management_info(json_url)

    # Llamar a la API de OpenAI para obtener la respuesta
    with st.chat_message("assistant"):
        messages = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
        response = openai.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=messages
        )
        response_text = response.choices[0].message.content
        
        # Enriquecer la respuesta con información del JSON si es necesario
        response_text = process_response(prompt, response_text, project_info)
        
        st.markdown(response_text)
    st.session_state.messages.append({"role": "assistant", "content": response_text})







