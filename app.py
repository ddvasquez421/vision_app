import os
import streamlit as st
import base64
from openai import OpenAI

# --- CSS for Renaissance Aesthetics ---
# You can adjust colors and fonts here
renaissance_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400..800;1,400..800&display=swap');

html, body, [data-testid="stAppViewContainer"] {
    background-color: #e5d8b0 !important; /* Un dorado pálido renacentista */
    color: #4f3d2c !important; /* Un marrón oscuro para el texto */
    font-family: 'EB Garamond', Georgia, Palatino Linotype, Palatino, serif !important; /* Fuente clásica con alternativas */
}


h1, h2, h3, h4, h5, h6 {
    color: #6b503d !important; /* Un marrón más rojizo para los encabezados */
    font-family: 'EB Garamond', Georgia, Palatino Linotype, Palatino, serif !important;
}

/* Ajustes menores para otros elementos si es necesario */
/* input, textarea, button { border-color: #6b503d; } */
/* button { background-color: #6b503d; color: white; } */

/* Asegurarse de que los componentes de Streamlit hereden el estilo de fuente y color */
div[data-testid] {
    font-family: 'EB Garamond', Georgia, Palatino Linotype, Palatino, serif !important;
    color: #4f3d2c !important;
}

/* Puedes añadir estilos de scrollbar si quieres un control total de la apariencia */
/*
::-webkit-scrollbar {
    width: 10px;
}
::-webkit-scrollbar-track {
    background: #f1f1f1;
}
::-webkit-scrollbar-thumb {
    background: #888;
}
::-webkit-scrollbar-thumb:hover {
    background: #555;
}
*/

</style>
"""

# Inject the CSS into the Streamlit app
st.markdown(renaissance_css, unsafe_allow_html=True)
# --- End CSS ---


# Function to encode the image to base64
def encode_image(image_file):
    # !!! LINEA CORREGIDA Y LIMPIADA DE CARACTERES ESPECIALES !!!
    return base64.b64encode(image_file.getvalue()).decode("utf-8")


st.set_page_config(page_title="Analisis de imagen", layout="centered", initial_sidebar_state="collapsed")

# Streamlit page setup
st.title("Análisis de Imagen: 👁️‍🗨️✨") # Cambié los emojis a algo más acorde

ke = st.text_input('Ingresa tu Clave del Saber (API Key)') # Lenguaje más clásico
os.environ['OPENAI_API_KEY'] = ke

# Retrieve the OpenAI API Key from secrets
api_key = os.environ.get('OPENAI_API_KEY') # Usar .get() es más seguro

# Initialize the OpenAI client with the API key
# Inicializa el cliente solo si hay una API key
client = None
if api_key:
    client = OpenAI(api_key=api_key)
else:
    st.warning("Por favor, proporciona tu Clave del Saber para proceder.")


# File uploader allows user to add their own image
st.markdown("Presenta aquí la imagen para ser estudiada:") # Texto más formal
uploaded_file = st.file_uploader("", type=["jpg", "png", "jpeg"], key="image_uploader")


if uploaded_file:
    # Display the uploaded image
    with st.expander("Imagen Presentada", expanded = True): # Texto más formal
        st.image(uploaded_file, caption=f"Ilustración: {uploaded_file.name}", use_container_width=True) # Texto más formal

# Toggle for showing additional details input
st.markdown("¿Deseas añadir observaciones adicionales para el análisis?") # Texto más formal
show_details = st.toggle("Sí, añadir observaciones", value=False) # Texto más formal

additional_details = None
if show_details:
    # Text input for additional details about the image, shown only if toggle is True
    additional_details = st.text_area(
        "Escribe aquí tus observaciones o contexto adicional:", # Texto más formal
        disabled=not show_details,
        key="additional_context"
    )

# Button to trigger the analysis
analyze_button = st.button("Emprender el Análisis", type="secondary") # Texto más formal

# Check if an image has been uploaded, if the API key is available, and if the button has been pressed
if uploaded_file is not None and api_key and client and analyze_button:

    with st.spinner("Procesando el análisis, aguarda un instante..."): # Texto más formal
        # Encode the image
        base64_image = encode_image(uploaded_file)

        # --- Renaissance Writing Style Prompt ---
        prompt_text = """Eres un erudito renacentista versado en las artes y las ciencias. Tu tarea es describir la imagen proporcionada con gran detalle y elocuencia, utilizando un lenguaje formal, culto y una prosa digna de la época del Renacimiento. Evita las jergas modernas y las contracciones. Enfócate en los elementos visuales, la posible simbología, la composición, la iluminación, los colores y la atmósfera, como si estuvieras redactando un tratado, una descripción para un inventario de obras de arte o una misiva para un mecenas. Tu descripción debe ser en español y debe reflejar un profundo conocimiento y aprecio por la belleza y el significado.

Procedo a presentarte la imagen para tu docto análisis:
""" # Instrucción detallada para el estilo y rol

        # The specific instruction to describe what's seen
        prompt_text += "Describe lo que se observa en esta imagen con la mayor precisión y belleza posibles."

        if show_details and additional_details:
            prompt_text += (
                f"\n\nConsidera asimismo el siguiente contexto adicional proporcionado por el mecenas para enriquecer tu análisis:\n{additional_details}"
            )
        # --- End Prompt Modification ---


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
            st.markdown("### Tratado sobre la Imagen:") # Título para la respuesta
            full_response = ""
            message_placeholder = st.empty()
            for completion in client.chat.completions.create(
                model="gpt-4o", messages=messages,
                max_tokens=1500, stream=True # Aumenté max_tokens un poco para descripciones más ricas
            ):
                # Check if there is content to display
                if completion.choices[0].delta.content is not None:
                    full_response += completion.choices[0].delta.content
                    # Usar markdown para que la respuesta respete el estilo de fuente y color
                    message_placeholder.markdown(full_response + "▌")
            # Final update to placeholder after the stream ends
            message_placeholder.markdown(full_response)

        except Exception as e:
            st.error(f"Ha ocurrido un infortunio al procesar el análisis: {e}") # Texto más formal
else:
    # Warnings for user action required
    if analyze_button: # Solo mostrar advertencias si se intentó analizar
        if not uploaded_file:
            st.warning("Por favor, dignate a cargar una imagen para su estudio.") # Texto más formal
        if not api_key or not client:
            st.warning("Se requiere tu Clave del Saber para invocar al oráculo.") # Texto más formal
