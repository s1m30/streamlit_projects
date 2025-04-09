from bs4 import BeautifulSoup as bsoup
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import requests
import sqlite3
import streamlit as st

def is_valid_website(website):
    response = requests.get(website)
    if response.status_code == 200:
        soup = bsoup(response.content, 'html.parser')
        title_tag = soup.find('title')
          # Parse the webpage content
        soup =bsoup(response.text, 'html.parser')

        # Extract the title from the HTML
        title_tag = soup.find("title")
        title = title_tag.text if title_tag else "No Title Found"
        return title
    else:
        return None

def get_titles():
    # Uncomment the below if you want to use the sqlite3 db to store your uploads on your PC
    # """
    # Fetches all unique document titles from the SQLite database.
    # Returns a list of titles or an empty list if no titles are found or the table doesn't exist.
    # """
    # conn = sqlite3.connect('content.db')
    # cursor = conn.cursor()
    # titles = []
    # try:
    #     cursor.execute("SELECT title FROM documents")
    #     titles = [row[0] for row in cursor.fetchall()]  # Extract titles from query results
    #     titles = list(set(titles)) # Make titles unique
    # except sqlite3.OperationalError: # Catch error if table does not exist
    #     pass # Return empty list if table does not exist
    # finally:
    #     conn.close()

    titles=[]
    try:
        titles=list(st.session_state.documents.keys())
    except:
        pass
    return titles


def get_content(title):
    # """
    # Retrieves content from the SQLite database based on the document title.
    # Returns a list containing the content of the document(s) matching the title.
    # """
    # conn = sqlite3.connect('content.db')
    # cursor = conn.cursor()
    # cursor.execute("SELECT content FROM documents Where title= ?", (title,))
    # content = cursor.fetchall()
    # conn.close()
    content=st.session_state.documents.get(title)
    return content
    
def show_titles_and_pages(contents):
    """
    Displays document titles in the sidebar using an expander.
    Allows users to select a document title and view its content page by page.
    Also displays the total length of the content in the sidebar.
    
    Arguments:
    - contents: A list of document contents.            
    """
    total_length = sum(len(content) for content in contents)
    with st.sidebar.expander("Pages"): 
        page_num=st.selectbox("Page Number",range(len(contents)),key="page_num", help="The page selected determines the quiz that is generated.")
        st.write(contents[page_num])
    # st.sidebar.write(total_length)
    
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

    Story.append(Paragraph("Questions", styles['Heading2']))
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
    return "quiz.pdf"
