import os
import streamlit as st
import base64
from openai import OpenAI

# Function to encode the image to base64
def encode_image(image_file):
    return base64.b64encode(image_file.getvalue()).decode("utf-8")

# Custom CSS to style the page
st.markdown("""
    <style>
    body {
        background-image: url('https://upload.wikimedia.org/wikipedia/commons/f/f8/The_Allegory_of_Truth_and_Falsehood%2C_by_Federico_Zuccari.jpg');  /* Fondo de imagen estilo renacentista */
        background-size: cover;  /* Asegura que la imagen cubra toda la página */
        color: #FFF8E1;  /* Color claro para el texto */
        font-family: 'Georgia', serif;  /* Fuente clásica diferente */
        margin: 0;
        padding: 0;
    }
    .stApp {
        background-color: rgba(0, 0, 0, 0.5);  /* Fondo oscuro semi-transparente para mejorar la legibilidad */
        padding: 20px;
        border-radius: 15px;
    }
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Georgia', serif;
        color: #FAF3E0;
    }
    .stTextInput, .stTextArea, .stButton {
        font-family: 'Georgia', serif;
        font-size: 16px;
        border-radius: 10px;
        padding: 10px;
    }
    .stButton>button {
        background-color: #B29D79;  /* Un color cálido para los botones */
        color: white;
        font-size: 16px;
        border-radius: 5px;
        padding: 10px;
    }
    .stTextInput input, .stTextArea textarea {
        background-color: #FAF3E0;
        color: #4B3C2F;  /* Color del texto */
        border: 2px solid #4B3C2F;
        font-size: 16px;
    }
    .stFileUploader {
        background-color: #B29D79;
        color: white;
        border-radius: 10px;
        font-size: 16px;
    }
    .stToggle {
        background-color: #B29D79;
        color: white;
        font-size: 16px;
        border-radius: 5px;
    }
    </style>
""", unsafe_allow_html=True)

st.set_page_config(page_title="Análisis de Imagen", layout="centered", initial_sidebar_state="collapsed")

# Streamlit page setup
st.title("Análisis de Imagen:🤖🏞️")
ke = st.text_input('Ingresa tu Clave')
os.environ['OPENAI_API_KEY'] = ke

# Retrieve the OpenAI API Key from secrets
api_key = os.environ['OPENAI_API_KEY']

# Initialize the OpenAI client with the API key
client = OpenAI(api_key=api_key)

# File uploader allows user to add their own image
uploaded_file = st.file_uploader("Upload an image", type=["jpg", "png", "jpeg"])

if uploaded_file:
    # Display the uploaded image
    with st.expander("Image", expanded=True):
        st.image(uploaded_file, caption=uploaded_file.name, use_container_width=True)

# Toggle for showing additional details input
show_details = st.toggle("Adiciona detalles sobre la imagen", value=False)

if show_details:
    # Text input for additional details about the image, shown only if toggle is True
    additional_details = st.text_area(
        "Adiciona contexto de la imagen aquí:",
        disabled=not show_details
    )

# Button to trigger the analysis
analyze_button = st.button("Analiza la imagen", type="secondary")

# Check if an image has been uploaded, if the API key is available, and if the button has been pressed
if uploaded_file is not None and api_key and analyze_button:

    with st.spinner("Analizando ..."):
        # Encode the image
        base64_image = encode_image(uploaded_file)

        prompt_text = ("Describe lo que ves en la imagen en español")

        if show_details and additional_details:
            prompt_text += (
                f"\n\nContexto adicional proporcionado por el usuario:\n{additional_details}"
            )

        # Create the payload for the completion request - CORRECTED FORMAT
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

        # Make the request to the OpenAI API
        try:
            # Stream the response
            full_response = ""
            message_placeholder = st.empty()
            for completion in client.chat.completions.create(
                model="gpt-4o", messages=messages,   
                max_tokens=1200, stream=True
            ):
                # Check if there is content to display
                if completion.choices[0].delta.content is not None:
                    full_response += completion.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")
            # Final update to placeholder after the stream ends
            message_placeholder.markdown(full_response)

        except Exception as e:
            st.error(f"An error occurred: {e}")
else:
    # Warnings for user action required
    if not uploaded_file and analyze_button:
        st.warning("Please upload an image.")
    if not api_key:
        st.warning("Por favor ingresa tu API key.")
