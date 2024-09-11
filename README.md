### **DocBot-AI: Intelligent Document Processing and Chatbot Application**

### **Summary:**
DocBot-AI is a sophisticated application designed to process various document formats (.pdf, .doc, .txt) and provide intelligent responses based on the content of these documents. Built using Streamlit and LangChain, this tool offers a user-friendly interface for document upload and querying, leveraging advanced AI models to deliver contextual answers.
![image](https://github.com/user-attachments/assets/243a9a78-87ef-4fc6-a4e0-604a95f4e7aa)

### **Features:**
- **Upload Document Files:** Supports PDF, DOC, and TXT file uploads.
- **Text Extraction:** Extracts text from various document formats.
- **Text Chunking:** Splits text into chunks for efficient processing.
- **Embedding Generation:** Uses OpenAI embeddings to create vector representations.
- **Vector Indexing:** Stores vectors in a FAISS index for quick searches.
- **Contextual Querying:** Provides answers to user queries based on document content.
- **Persistent Storage:** Saves FAISS index locally for state retention and improved performance.
### **Project Structure:**
```
DocBot-AI/
│
├── faiss_store             # Directory storing FAISS vector index
├── .DS_Store               # macOS system file (typically ignored)
├── .env                    # Environment variables file (e.g., API keys)
├── Dockerfile              # Dockerfile for containerizing the application
├── main.py                # Main application file with Streamlit and processing logic
└── requirements.txt       # Python dependencies for the project
```
- **`faiss_store`**: Contains the FAISS vector index used for storing and querying document embeddings efficiently.
- **`.DS_Store`**: A macOS system file that stores custom attributes of a folder, typically ignored in version control.
- **`.env`**: Holds environment-specific variables such as API keys and configuration settings required for the application.
- **`Dockerfile`**: Defines the steps to build a Docker image for the application, including installing dependencies and setting up the runtime environment.
- **`main.py`**: The primary script that integrates Streamlit for the user interface and contains the core logic for document processing, text extraction, and interaction with AI models.
- **`requirements.txt`**: Lists the Python packages and their versions needed to run the application, ensuring consistent and reproducible environment setup.

This project provides a comprehensive solution for document processing and querying, leveraging modern AI technologies to enhance user interaction with document content.
