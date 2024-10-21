# CyborBot

Welcome to **CyborBot**! This repository contains a framework for creating a chatbot powered by advanced machine learning techniques. The bot utilizes embeddings, a FAISS vector database, and a self-attention model to provide answers to user queries.

## Features

- **Data Embedding**: Generate embeddings from your data using `langchain_helper.py`.
- **FAISS Vector Database**: Store and retrieve embeddings efficiently.
- **Training with Ollama**: Utilize Ollama to train your data and improve response quality.
- **User Interface**: A Streamlit app to interact with the chatbot and ask questions.
- **Custom Self-Attention Model**: Implemented in `tejas_gpt_ED.py`, this model is capable of tokenization and embedding creation.

## File Descriptions

- **langchain_helper.py**: 
  - Handles the creation of embeddings and stores them in a FAISS vector database.
  - Integrates with Ollama for training the data and generating responses.

- **main.py**: 
  - The main entry point of the application.
  - Utilizes functions from `langchain_helper.py` to fetch answers based on user input.
  - Implements a Streamlit app for a user-friendly interface.

- **tejas_gpt_ED.py**: 
  - A standalone script designed for tokenization and embedding creation.
  - Implements a self-attention model to enhance the training process.

- **requirements.txt**: 
  - Lists the required Python packages for running the project.

## Installation

To set up the CyborBot, follow these steps:

1. Clone the repository:
   ```bash
   git clone https://github.com/JAISHIVAWASTHI/AI-Projects/Cybor_Bot/CyborBot_2.git
   cd CyborBot_2
   ```

2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Start the Streamlit app:
   ```bash
   streamlit run main.py
   ```

2. Open your web browser and navigate to `http://localhost:8501` to interact with the chatbot.

3. Use the input field to ask questions, and the bot will provide answers based on the trained data.

## Contributing

Contributions are welcome! If you'd like to contribute to the project, please follow these steps:

1. Fork the repository.
2. Create a new branch:
   ```bash
   git checkout -b feature/YourFeature
   ```
3. Make your changes and commit them:
   ```bash
   git commit -m "Add your message"
   ```
4. Push to the branch:
   ```bash
   git push origin feature/YourFeature
   ```
5. Submit a pull request.
