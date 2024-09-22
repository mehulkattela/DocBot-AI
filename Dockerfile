# Use an official Python runtime as a parent image
FROM python:3.9-bullseye

# Copy the current directory contents into the container at /DocBotApp
COPY . /DocBotApp/

# Set the working directory in the container
WORKDIR /DocBotApp

# Install system dependencies
RUN apt-get update && apt-get install -y \
    antiword \
    libreoffice \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port that the Streamlit app will run on
EXPOSE 8501

# Run Streamlit when the container launches
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]