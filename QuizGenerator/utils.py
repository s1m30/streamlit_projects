import sqlite3
from ollama import chat
import langchain_text_splitters as splitter
from tempfile import NamedTemporaryFile
from pydantic import BaseModel
import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

class Quiz(BaseModel):
    question: str
    choices: list[str]
    correct_answer: str
    explanation:str
class Quizlist(BaseModel):
    quizzes:list[Quiz]
    
def save_to_database(title, content):
    """
    Saves document title and content to an SQLite database.
    Initializes the database and table if they don't exist.
    """
    # # Connect to an SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect('content.db')
    # # Create a cursor object using the cursor() method
    cursor = conn.cursor()
    # # Create table
    cursor.execute('''CREATE TABLE IF NOT EXISTS documents
                  (title text, content text)''')
    # # Insert a row of data
    cursor.execute("INSERT INTO documents (title,content) VALUES (?, ?)", (title, content))
    # # Save (commit) the changes
    conn.commit()
    # # Close the connection
    conn.close()

def get_titles():
    """
    Fetches all unique document titles from the SQLite database.
    Returns a list of titles or an empty list if no titles are found or the table doesn't exist.
    """
    conn = sqlite3.connect('content.db')
    cursor = conn.cursor()
    titles = []
    try:
        cursor.execute("SELECT title FROM documents")
        titles = [row[0] for row in cursor.fetchall()]  # Extract titles from query results
        titles = list(set(titles)) # Make titles unique
    except sqlite3.OperationalError: # Catch error if table does not exist
        pass # Return empty list if table does not exist
    finally:
        conn.close()
    return titles


def get_content(title):
    """
    Retrieves content from the SQLite database based on the document title.
    Returns a list containing the content of the document(s) matching the title.
    """
    conn = sqlite3.connect('content.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT content FROM documents Where title= ?", (title,))
    content = [row[0] for row in cursor.fetchall()]
    conn.close()
    return content
    

def generate_quiz(content_text, question_num):
    """
    Generates a multiple-choice quiz using the Ollama language model.
    The quiz is based on the provided content text and the desired number of questions.
    It formats the prompt for Ollama, sends the request, and parses the JSON response
    into a Quizlist object.
    """
    SYSTEM_PROMPT= f"""#Instruction
                        You are a professor. Using the provided lecture content, create a Master-level multiple-choice exam in strict JSON format that includes exactly {question_num} questions. 
                        Ensure the structure is:
                        [{{'question': '...', 'choices': ['...'], 'correct_answer': '...', 'explanation': '...'}}, ...]\n
                        #Further Instructions
                        -Avoid excessive whitespaces
                        -Always return output as JSON format
                        
                        #Content:\n
                        {content_text}"""
                        
    response = chat(
    messages=[{'role': 'user','content': SYSTEM_PROMPT}],
    model='llama3',
    format=Quizlist.model_json_schema(),
    )
    
    # Extract response content (which should be a JSON string)
    try:
        # quiz_json = json.loads(response['message']['content'])  # Parse JSON
        # quiz_objects = [Quiz(**q) for q in quiz_json]  # Convert to Pydantic objects
        # return quiz_objects
        quiz_obj = Quizlist.model_validate_json(response.message.content)
        return quiz_obj

    except Exception as e:
        print("Error parsing response:", e)
        return None
    # quiz = Quiz.model_validate_json(response.message.content)
    # return (quiz)

def reduced_prompt(contents):
    """
    Reduces the length of the combined content to be within a token limit (e.g., 4500 characters).
    This is to prevent exceeding the language model's input token limit.
    """
    prompt="".join(contents)
    if len(prompt)>4500:
        prompt=prompt[:4500]
    return prompt
    
def save_pdf(parsed_quiz):
    """
    Generates a PDF file of the quiz from parsed quiz data.
    Uses ReportLab library to create the PDF document, including questions,
    answer choices as bullet points, and answer explanations.
    """
    doc = SimpleDocTemplate("quiz.pdf", pagesize=letter)
    styles = getSampleStyleSheet()
    Story = []
    question_style = ParagraphStyle(
        name='QuestionStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=14,
        spaceAfter=6
    )
    answer_style = ParagraphStyle(
        name='AnswerStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=12,
        spaceAfter=6
    )
    explanation_style = ParagraphStyle(
        name='ExplanationStyle',
        parent=styles['Italic'],
        fontName='Times-Italic',
        fontSize=10,
        leading=12,
        spaceAfter=12
    )

    for i, quiz_item in enumerate(parsed_quiz):
        question_num = i + 1
        question_text = f"{question_num}. {quiz_item['question']}"
        Story.append(Paragraph(question_text, question_style))

        choices_list = [(choice) for choice in quiz_item['choices']] # bulleted list of choices
        Story.append(ListFlowable([Paragraph(choice, answer_style) for choice in choices_list], bulletType='bullet', start='bulletchar'))
        Story.append(Spacer(1, 0.2*inch)) # space after each question

    Story.append(Paragraph("Answers and Explanations", styles['Heading2']))
    for i, quiz_item in enumerate(parsed_quiz):
        question_num = i + 1
        answer_text = f"{question_num}. Correct Answer: {quiz_item['correct_answer']}"
        Story.append(Paragraph(answer_text, question_style))
        explanation_text = f"Explanation: {quiz_item['explanation']}"
        Story.append(Paragraph(explanation_text, explanation_style))
        Story.append(Spacer(1, 0.2*inch)) # space after each answer explanation

    doc.build(Story)
    return f"{st.session_state.selected_title}.pdf"
