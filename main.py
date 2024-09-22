import os
import streamlit as st
import time
import pymupdf as fitz
import subprocess
import os
import logging
from langchain import OpenAI
from langchain.schema import Document
from langchain.chains import RetrievalQA
from langchain.chains.qa_with_sources.loading import load_qa_with_sources_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from dotenv import load_dotenv

# configuring logging module
logging.basicConfig(filename = 'main.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# loads environment variables from .env
load_dotenv()
logging.info("Environment variables loaded.")

# Function to extract text from PDF
def extract_text_from_pdf(pdf_file):
    logging.info("Starting to extract text from PDF.")
    text = ""
    with fitz.open(stream=pdf_file.read(), filetype="pdf") as doc:
        for page_num in range(doc.page_count):
            page = doc.load_page(page_num)
            text += page.get_text()
    logging.info("Completed text extraction from PDF.")
    return text

# Function to extract text from DOC
def extract_text_from_doc(doc_file):
    logging.info("Starting to extract text from DOC.")
    # Save the uploaded .doc file to a temporary location
    temp_doc_file = "/tmp/temp.doc"    
    # Write the uploaded .doc file to the temporary file
    with open(temp_doc_file, "wb") as temp_file:
        temp_file.write(doc_file.read())
    # Use antiword to convert .doc to plain text
    try:
        result = subprocess.run(
            ['antiword', temp_doc_file],
            capture_output=True,
            text=True,
            check=True
        )
        text = result.stdout
        logging.info("Text extraction from DOC completed successfully.")
    except subprocess.CalledProcessError as e:
        error_message = e.stderr if e.stderr else str(e)
        print(f"Error during conversion: {error_message}")
        logging.error(f"Error during DOC extraction: {error_message}")
        text = ""
    finally:
        # Clean up the temporary file
        os.remove(temp_doc_file)
    
    return text

#Creating a streamlit application
st.title("SmartDoc Assistant 🤖")
st.sidebar.title("Documents Upload")

#Setting up LLM model
llm=OpenAI (temperature = 0.9, max_tokens = 500)
main_placeholder = st.empty()

#Input Docs from sidebar
uploaded_file = st.sidebar.file_uploader("Upload a file", type=["txt", "pdf", "doc"])
process_docs_clicked = st.sidebar.button("Process Docs")

if process_docs_clicked:
    if uploaded_file is None:
        logging.warning("No file uploaded.")
        st.error("Please upload a file first... ❌ ❌ ❌")
    else:
        file_type = uploaded_file.type
        logging.info(f"Uploaded file type: {file_type}")
        file_content=""
        if file_type == "application/pdf":
            file_content = extract_text_from_pdf(uploaded_file)
        elif file_type == "application/msword":
            file_content = extract_text_from_doc(uploaded_file)
        elif file_type == "text/plain":
            # Handle text files with different encodings if utf-8 fails
            try:
                file_content = uploaded_file.read().decode('utf-8')
            except UnicodeDecodeError:
                file_content = uploaded_file.read().decode('ISO-8859-1')

        #Processing Docs if button is clicked
        if process_docs_clicked and file_content:
            logging.info("Processing the uploaded document.")
            st.session_state.messages = []
            main_placeholder.text("Data Loading... Started... ✅ ✅ ✅")
            # Step to split the text into chunks
            text_splitter = RecursiveCharacterTextSplitter(
                separators=['\n\n', '\n', '.', '.'],
                chunk_size = 1000
            )
            main_placeholder.text("Text splitter... Started... ✅ ✅ ✅")
            docs = text_splitter.split_text(file_content)
            documents = [Document(page_content=chunk) for chunk in docs]
            logging.info("Text splitting completed.")
            # Step to embed the text and save it to FAISS index
            embeddings = OpenAIEmbeddings()
            vectorstore_openai = FAISS.from_documents(documents, embeddings)
            main_placeholder.text("Embedding vector index build in progress... ✅ ✅ ✅")
            time.sleep(2)
            # Save the FAISS index locally creating faiss_store dir. This allows you to persist the index so that it can be reloaded later without needing to recompute the embeddings and rebuild the index.
            vectorstore_openai.save_local("faiss_store")
            main_placeholder.text("Embedding vector index saved locally... ✅ ✅ ✅")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("What is up?"):
    logging.info(f"User input received: {prompt}")
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Loading vector index
    vectorstore = FAISS.load_local("faiss_store", OpenAIEmbeddings(), allow_dangerous_deserialization=True)
    chain = RetrievalQA.from_llm(llm = llm, retriever = vectorstore.as_retriever())
    result = chain({"query": prompt}, return_only_outputs=True)
    logging.info(f"Response generated for user query: {result}")
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(result['result'])
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": result['result']})