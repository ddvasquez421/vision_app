import os
import streamlit as st
import base64
from openai import OpenAI

# Function to encode the image to base64
def encode_image(image_file):
    return base64.b64encode(image_file.getvalue()).decode("utf-8")

# Establecer la configuración de la página
st.set_page_config(page_title="Análisis de Imagen", layout="centered", initial_sidebar_state="collapsed")

# Cambiar estilo para darle un aire renacentista
st.markdown("""
    <style>
        /* Fondo en tonos cálidos, como los usados en las pinturas del Renacimiento */
        body {
            background-color: #f5e1a4;
            font-family: 'Georgia', serif;
            color: #3e2a47;
        }

        /* Títulos con un estilo clásico */
        .title {
            font-size: 3em;
            font-family: 'Georgia', serif;
            color: #4a2c3e;
            text-align: center;
            margin-bottom: 50px;
        }

        /* Estilo de los botones */
        .stButton>button {
            background-color: #b88b4a;
            color: #ffffff;
            font-size: 18px;
            border-radius: 12px;
            border: none;
            padding: 15px 40px;
            font-family: 'Georgia', serif;
            text-transform: uppercase;
        }

        /* Estilo para los encabezados */
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Georgia', serif;
            color: #4a2c3e;
            text-align: center;
        }

        /* Estilo de las entradas de texto y área de texto */
        .stTextInput>div>input, .stTextArea>div>textarea {
            background-color: #fff3e6;
            color: #3e2a47;
            font-family: 'Georgia', serif;
            border: 2px solid #b88b4a;
            border-radius: 8px;
            font-size: 16px;
            padding: 12px;
        }

        /* Color del contorno de los elementos de selección */
        .stFileUploader {
            border: 2px solid #b88b4a;
            border-radius: 10px;
            padding: 10px;
        }

        /* Estilo del expander (para la imagen) */
        .stExpander {
            background-color: #f0e2c2;
            border: 1px solid #b88b4a;
            border-radius: 8px;
        }

        /* Estilo para el contenedor de la imagen */
        .stImage {
            border-radius: 15px;
            border: 5px solid #b88b4a;
            padding: 20px;
            background-color: #fff3e6;
        }
    </style>
""", unsafe_allow_html=True)

# Título principal
st.markdown('<h1 class="title">Análisis de Imagen Renacentista</h1>', unsafe_allow_html=True)

ke = st.text_input('Ingresa tu Clave', placeholder='Tu API key aquí...')
os.environ['OPENAI_API_KEY'] = ke

# Recuperar la clave API de OpenAI
api_key = os.environ['OPENAI_API_KEY']

# Inicializar el cliente de OpenAI
client = OpenAI(api_key=api_key)

# Subir una imagen
uploaded_file = st.file_uploader("Sube una imagen", type=["jpg", "png", "jpeg"])

if uploaded_file:
    # Mostrar la imagen subida
    with st.expander("Imagen", expanded=True):
        st.image(uploaded_file, caption=uploaded_file.name, use_container_width=True)

# Entrada adicional de detalles
show_details = st.toggle("Añadir detalles sobre la imagen", value=False)

if show_details:
    additional_details = st.text_area(
        "Añade contexto de la imagen aquí:",
        disabled=not show_details
    )

# Botón para iniciar el análisis
analyze_button = st.button("Analiza la imagen", type="primary")

# Análisis cuando la imagen es subida, la clave API está disponible y el botón es presionado
if uploaded_file is not None and api_key and analyze_button:

    with st.spinner("Analizando ..."):
        # Codificar la imagen
        base64_image = encode_image(uploaded_file)
    
        prompt_text = ("Describe lo que ves en la imagen en español.")
    
        if show_details and additional_details:
            prompt_text += f"\n\nDetalles adicionales proporcionados por el usuario:\n{additional_details}"
    
        # Crear el mensaje para la solicitud de la API
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_text},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    },
                ],
            }
        ]
    
        # Solicitar la API de OpenAI
        try:
            full_response = ""
            message_placeholder = st.empty()
            for completion in client.chat.completions.create(
                model="gpt-4o", messages=messages,   
                max_tokens=1200, stream=True
            ):
                if completion.choices[0].delta.content is not None:
                    full_response += completion.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
    
        except Exception as e:
            st.error(f"Se produjo un error: {e}")
else:
    # Advertencias si falta acción por parte del usuario
    if not uploaded_file and analyze_button:
        st.warning("Por favor, sube una imagen.")
    if not api_key:
        st.warning("Por favor ingresa tu clave de API.")
