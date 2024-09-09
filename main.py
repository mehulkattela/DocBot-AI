import os
import streamlit as st
import time
import fitz
import subprocess
import os
import pypandoc
from pyth.plugins import plaintext
from io import BytesIO
from langchain_community.document_loaders import PyPDFLoader
from langchain import OpenAI
from langchain.schema import Document
from langchain.chains import RetrievalQA
from langchain.chains.qa_with_sources.loading import load_qa_with_sources_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import UnstructuredURLLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS

from dotenv import load_dotenv
#loads environment variables from .env
load_dotenv()

# Function to extract text from PDF
def extract_text_from_pdf(pdf_file):
    text = ""
    with fitz.open(stream=pdf_file.read(), filetype="pdf") as doc:
        for page_num in range(doc.page_count):
            page = doc.load_page(page_num)
            text += page.get_text()
    return text

# Function to extract text from DOC
def extract_text_from_doc(doc_file):
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
    except subprocess.CalledProcessError as e:
        error_message = e.stderr if e.stderr else str(e)
        print(f"Error during conversion: {error_message}")
        text = ""
    finally:
        # Clean up the temporary file
        os.remove(temp_doc_file)
    
    return text

#Creating a streamlit application
st.title("SmartDoc Assistant 🤖")
st.sidebar.title("Documents Upload")

#Input Docs from sidebar
uploaded_file = st.sidebar.file_uploader("Upload a file", type=["txt", "pdf", "doc"])
process_docs_clicked = st.sidebar.button("Process Docs")

if uploaded_file is not None:
    st.session_state.messages = []
    file_type = uploaded_file.type
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

#Setting up LLM model
llm=OpenAI (temperature = 0.7, max_tokens = 500)
main_placefolder = st.empty()

#Processing Docs if button is clicked
if process_docs_clicked and file_content:
    main_placefolder.text("Data Loading... Started... ✅ ✅ ✅")
    # Step to split the text into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        separators=['\n\n', '\n', '.', '.'],
        chunk_size = 1000
    )
    main_placefolder.text("Text splitter... Started... ✅ ✅ ✅")
    docs = text_splitter.split_text(file_content)
    documents = [Document(page_content=chunk) for chunk in docs]
    # Step to embed the text and save it to FAISS index
    embeddings = OpenAIEmbeddings()
    vectorstore_openai = FAISS.from_documents(documents, embeddings)
    main_placefolder.text("Embedding vector index build in progress... ✅ ✅ ✅")
    time.sleep(2)
    # Save the FAISS index locally creating faiss_store dir. This allows you to persist the index so that it can be reloaded later without needing to recompute the embeddings and rebuild the index.
    vectorstore_openai.save_local("faiss_store")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("What is up?"):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Loading vector index
    vectorstore = FAISS.load_local("faiss_store", OpenAIEmbeddings(), allow_dangerous_deserialization=True)
    chain = RetrievalQA.from_llm(llm = llm, retriever = vectorstore.as_retriever())
    result = chain({"query": prompt}, return_only_outputs=True)  #{"answer":"", "sources":[]}
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(result['result'])
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": result})