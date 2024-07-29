import streamlit as st
import pathlib
from PIL import Image
import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("API_KEY")

genai.configure(api_key=API_KEY)

generation_config = {
    "temperature": 0,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 10000,
}

MODEL_NAME = "gemini-1.5-pro"

framework = "Bootstrap"  

model = genai.GenerativeModel(
    model_name=MODEL_NAME,
    generation_config=generation_config,
)

chat_session = model.start_chat(history=[])

def send_message_to_model(message, image_path):
    image_input = {
        'mime_type': 'image/png',
        'data': pathlib.Path(image_path).read_bytes()
    }
    response = chat_session.send_message([message, image_input])
    return response.text

# Streamlit app
def main():
    st.title("Img to Code (html)")
    st.subheader('API Testing')

    uploaded_file = st.file_uploader("Choose an image...", type=["png"])

    if uploaded_file is not None:
        try:
            image = Image.open(uploaded_file)
            st.image(image, caption='Uploaded Image.', use_column_width=True)

            if image.mode == 'RGBA':
                image = image.convert('RGB')

            temp_image_path = pathlib.Path("temp_image.png")
            image.save(temp_image_path, format="PNG")

            # Generate HTML
            if st.button("Generate HTML"):
                st.write("Generating website...")
                html_prompt = f"Create an HTML file based on the provided image. Include {framework} CSS within the HTML file to style the elements. Make sure the colors used are the same as the original UI. The UI needs to be responsive and mobile-first, matching the original UI as closely as possible. Do not include any explanations or comments. Avoid using ```html. and ``` at the end. ONLY return the HTML code with inline CSS."
                initial_html = send_message_to_model(html_prompt, temp_image_path)
                st.code(initial_html, language='html')

                st.write("Refining website...")
                refine_html_prompt = f"Validate the following HTML code based on the provided image and provide a refined version of the HTML code with {framework} CSS that improves accuracy, responsiveness, and adherence to the original design. ONLY return the refined HTML code with inline CSS. Avoid using ```html. and ``` at the end. Here is the initial HTML: {initial_html}"
                refined_html = send_message_to_model(refine_html_prompt, temp_image_path)
                st.code(refined_html, language='html')

                with open("index.html", "w") as file:
                    file.write(refined_html)
                st.success("HTML file 'index.html' has been created.")
                st.download_button(label="Download HTML", data=refined_html, file_name="index.html", mime="text/html")
        except Exception as e:
            st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()