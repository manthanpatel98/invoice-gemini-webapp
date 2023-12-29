from dotenv import load_dotenv
load_dotenv() ## Load all the environment variables from .env


import fitz  # PyMuPDF
from io import BytesIO
import streamlit as st
import os
import PyPDF2 as pdf
from PIL import Image
import google.generativeai as genai

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

## Load Gemini Pro Vision Model
model = genai.GenerativeModel('gemini-pro-vision')

def get_gemini_response(input,pdf_images,user_prompt):
    response = model.generate_content([input,pdf_images[0],user_prompt])
    return response.text




def input_image_details(uploaded_file):
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()

        image_parts = [
            {
                "mime_type": uploaded_file.type,
                "data":bytes_data
            }
        ]
        return image_parts
    else:
        raise FileNotFoundError("No File uploaded")
    


def read_pdf(uploaded_file):
    try:
        with fitz.open(uploaded_file) as pdf_document:
            images = []
            for page_number in range(pdf_document.page_count):
                page = pdf_document[page_number]
                image = page.get_pixmap()
                #pil_image = Image.frombytes("RGB", (image.width, image.height), image.samples)
                pil_image = Image.frombytes("RGB", (image.width, image.height), image.samples)
                images.append(pil_image)
            return images
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return None

## Streamlit App
st.set_page_config(page_title="Billing Extractor")
st.header("Multilanguage Extractor")
input = st.text_input("Input Prompt: ", key="input")
uploaded_file = st.file_uploader("Choose a file....", type=["jpg","jpeg","png","pdf"])

if uploaded_file is not None:
        
    st.header("Displaying PDF Pages")

    pdf_images = read_pdf(uploaded_file)
    if pdf_images:
        for i, image in enumerate(pdf_images):
            st.image(image, caption=f"Page {i + 1}", use_column_width=True)
#    image = open(uploaded_file,'r')
#    st.image(image, caption = "upload Image.", use_column_width=True)

submit = st.button("Tell me about the file")

input_prompt = """
You are an expert in understanding invoices. We will upload an image as invoice and you will have to answer any questions based on the uploaded invoice image
"""

## If submit button is clicked

if submit:
    image_data = input_image_details(uploaded_file)
    response = get_gemini_response(input_prompt,image_data,input)
    st.subheader("The Response is:")
    st.write(response)







