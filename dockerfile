# Use the official Python image from the Docker Hub
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install some additional packages and update essential packages
RUN apt-get update && apt-get install -y build-essential

# Copy the requirements.txt file into the container
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install some additional required elements for nltk
# RUN python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"

# Copy the rest of the application code into the container
COPY . .

# Expose the port that Streamlit will run on
EXPOSE 8502

# Définir le point d'entrée
RUN python -c "from server.db.db import init_db; init_db"

# Command to run the Streamlit app on port 8502
CMD ["streamlit", "run", "client/app.py", "--server.port=8502"]