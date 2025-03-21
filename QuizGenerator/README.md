# Personal Quiz Generator with Ollama and Streamlit

## Overview

This project is a Streamlit application that allows you to generate personalized quizzes from your study materials. It uses:

- **Streamlit:** To create an interactive and user-friendly web interface.
- **Ollama:** To run open-source language models locally for quiz generation.
- **Langchain:** To process and load documents from various file formats.

You can upload your documents (PDF, TXT, DOCX), and the application will generate multiple-choice quizzes based on the content, helping you to test your understanding and improve your study process.

## Prerequisites

Before running this application, ensure you have the following installed:

1.  **Python:** Python 3.x is required. You can download it from [https://www.python.org/](https://www.python.org/).
2.  **Ollama:** Ollama needs to be installed and running on your system. Follow the installation instructions at [https://ollama.com/](https://ollama.com/). Make sure Ollama is running before starting the Streamlit app.

## Installation

1.  **Clone the repository:**

    ```bash
    git clone [https://github.com/s1m30/streamlit_projects]
    cd Quizgenerator
    ```

2.  **Navigate to the project directory:**

    ```bash
    cd main app # Assuming your Streamlit app files are in 'main app' directory
    ```

3.  **Create a virtual environment (recommended):**

    ```bash
    python -m venv venv
    ```

    - On Windows, activate the virtual environment:

      ```bash
      venv\Scripts\activate
      ```

    - On macOS and Linux:

      ```bash
      source venv/bin/activate
      ```

4.  **Install Python dependencies:**

    ```bash
    pip install streamlit langchain-community ollama pdfminer.six pydantic reportlab
    ```

## Running the Application

To start the Streamlit application, run the following command in your terminal from the `main app` directory:

```bash
streamlit run app.py
```

This will open the Quiz Generator app in your web browser (usually at `http://localhost:8501`).

## Usage

1.  **Upload Study Materials:** In the sidebar, use the file uploader to upload your study documents (PDF, TXT, DOCX files are supported). Click "Load Sources" to process the uploaded files.
2.  **Select Document:** Choose the uploaded document from the "Selected Documents" dropdown in the sidebar. The content of the selected document will be displayed.
3.  **Generate Quiz:** Use the slider to select the number of questions you want to generate. Click the "Generate Quiz" button.
4.  **Take Quiz:** The quiz questions will be displayed interactively. Select your answer for each question and click "Submit" to check your answer and see the explanation. Use the "Next" button to proceed to the next question.
5.  **Download Quiz:** After the quiz is generated (or completed), a "Download Quiz PDF" button will appear, allowing you to download a PDF version of the quiz.
