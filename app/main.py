import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage
from langchain_community.llms import Ollama
from dotenv import load_dotenv
import tensorflow as tf
from PIL import Image
import numpy as np
import io
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
import logging
import ast

load_dotenv()

# Set up Ollama model
llm = Ollama(model="tinyllama")

log = logging.getLogger(__name__)

# Load Keras model
MODEL = tf.saved_model.load('mobilenet_model')
MODEL_SERVING_FUNCTION = MODEL.signatures['serving_default']

# App config
st.set_page_config(page_title="Deep Waste", page_icon="♻️")

# Styled Title with Animation
st.markdown("""
    <style>
    @keyframes colorChange {
        0% { color: #4CAF50; }    /* Initial Green */
        20% { color: #66BB6A; }   /* Medium Green */
        40% { color: #81C784; }   /* Light Green */
        60% { color: #A5D6A7; }   /* Pale Green */
        80% { color: #66BB6A; }   /* Medium Green */
        100% { color: #4CAF50; }  /* Final Green */
    }
    .title {
        font-size: 40px;
        font-weight: bold;
        animation: colorChange 2s ease-in-out forwards; /* Faster animation */
    }
    </style>
    <h1 class="title">Garbo: Your Waste Assistant</h1>
""", unsafe_allow_html=True)

st.markdown("""
Meet **Garbo**, your friendly assistant for waste management and recycling. 
            With **Deep Waste**, Garbo helps you sort, classify, and dispose of waste efficiently. Here's how Garbo can assist you:

- **Ask Questions**: Get immediate answers to your waste management queries.
- **Upload Images**: Classify waste items by uploading images for accurate sorting.

Together, we can make recycling easier and more effective. Let's get started!
""")

chatbot_icon_path = "app/assets/garbo.jpeg"  # Replace with your icon URL

def get_response(user_query, chat_history):
    # Create the prompt based on chat history and user query
    template = """
    You are a helpful assistant. Answer the following questions considering the history of the conversation:

    Chat history: {chat_history}

    User question: {user_question}
    """
    prompt = template.format(
        chat_history="\n".join([msg.content for msg in chat_history]),
        user_question=user_query
    )

    # Invoke the Ollama model with the prompt
    result = llm.invoke(prompt)
    return result.strip()  # Ensure there's no leading or trailing whitespace


def run(input_data):
    """Makes a prediction using the trained ML model."""
    log.info("input_data:%s", input_data)

    # Ensure MODEL is loaded
    if MODEL is None or MODEL_SERVING_FUNCTION is None:
        raise ValueError("Model is not loaded. Please call init() first.")

    # Load and preprocess the image
    img_path = input_data['image']
    img = load_img(img_path, target_size=(224, 224))
    img_array = np.expand_dims(img, axis=0)
    img_array = preprocess_input(img_array)

    # Make a prediction using the serving_default signature
    input_tensor = tf.convert_to_tensor(img_array, dtype=tf.float32)
    predictions = MODEL_SERVING_FUNCTION(input_tensor)

    # Log the keys of the predictions dictionary
    log.debug(f"Prediction keys: {predictions.keys()}")
    # Extract the prediction results
    prediction_key = 'dense_1'
    waste_pred = predictions[prediction_key].numpy()[0]
    waste_types = ast.literal_eval(input_data['classifiers'][0])
    index = np.argmax(waste_pred)
    waste_label = waste_types[index]
    accuracy = "{0:.2f}".format(waste_pred[index] * 100)
    
    return {"accuracy": accuracy, "label": waste_label}

# Session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        AIMessage(content="Hello!"),
    ]

# Tabs
tab1, tab2 = st.tabs(["Ask a Question", "Classify Waste Image"])

# Conversation tab
with tab1:
    chat_container = st.container()
    for message in st.session_state.chat_history:
        if isinstance(message, AIMessage):
            with chat_container.chat_message("AI", avatar=chatbot_icon_path):
                st.write(message.content)
        elif isinstance(message, HumanMessage):
            with chat_container.chat_message("Human"):
                st.write(message.content)

    user_query = st.chat_input("Type your message here...")
    if user_query:
        st.session_state.chat_history.append(HumanMessage(content=user_query))

        with chat_container.chat_message("Human"):
            st.markdown(user_query)

        # Show spinner while getting the response
        with st.spinner("Generating response..."):
            response = get_response(user_query, st.session_state.chat_history)

        st.session_state.chat_history.append(AIMessage(content=response))

        with chat_container.chat_message("AI", avatar=chatbot_icon_path):
            st.write(response)

# Image classification tab
with tab2:
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        image = Image.open(uploaded_file).convert('RGB')
        st.image(image, caption='Uploaded Image.', use_column_width=True)
        st.write("")
        # st.write("Classifying...")
        with st.spinner("Classifying image..."):
            # Save the uploaded image to a temporary file
            temp_file_path = "./temp_image.jpg"
            image.save(temp_file_path)
            
            # Prepare input data for the run function
            input_data = {
                'image': temp_file_path,
                'classifiers': ["['battery', 'biological', 'cardboard', 'clothes', 'glass', 'metal', 'paper','plastic','shoes','trash']"]
            }
            
            prediction = run(input_data)
            st.markdown(f"""
                <div style="border: 2px solid #4CAF50; padding: 10px; border-radius: 10px; margin-top: 0px; margin-bottom:15px;">
                    <h3 style="color: #4CAF50;">Prediction Result</h3>
                    <p><strong>Waste Label:</strong> {prediction['label']}</p>
                    <p><strong>Accuracy:</strong> {prediction['accuracy']}%</p>
                    <p style="color: #e4a11b;"><strong>⚠️Note:</strong> We're learning, but sometimes we make mistakes! Submit waste photos through our app to help us learn and reduce waste ♻️. Let's protect our planet together 🌍💜!</p>
                </div>
            """, unsafe_allow_html=True)


# Privacy Note
st.markdown("""
**Note:** While Garbo strives to provide accurate information, occasional mistakes may occur. Please refer to our [Privacy Policy](https://www.dwaste.live/privacy-policy/) for more details.
""")


