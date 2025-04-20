from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import requests
import streamlit as st
from enum import Enum
from loaders import Loader

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
    with st.sidebar.expander("Pages"): 
        page_num=st.selectbox("Page Number",range(len(contents)),key="page_num", help="The page selected determines the quiz that is generated.")
        st.write(contents[page_num])

def upload_file():
    """
    Creates a file uploader in the sidebar using Streamlit.
    Allows users to upload multiple files of specified types (txt, pdf, docx).
    When the 'Load Sources' button is pressed, it calls the save_sources function
    to process and save the uploaded files.
    """
    files = st.file_uploader("Upload file sources", accept_multiple_files=True,type=["txt", "pdf", "docx"])
    web=st.text_input("Input a website source")
    if st.button("Load Sources"):
        with st.spinner("The Quill is taking a look"):
            Loader(files,web).load_sources()

def save_pdf(parsed_quiz):
    """
    Uses ReportLab library to create a PDF document from parsed quiz data, including questions,
    answer choices as bullet points, and explanations.
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

class StyleOptions(Enum):
    Factual="Straightforward fact-based questions.",
    Mathematical="Questions involve calculations, formulas, or logical problem-solving.",
    Coding="Generates coding challenges or theoretical programming questions.",
    Case_Study="Presents a scenario and asks for analysis or recommendations.",
    Conceptual="Tests understanding of the fundamental ideas behind a topic.",
    Theoretical="Questions focus on definitions, concepts, and explanations",
    Technical="Focuses on implementation, tools, and methodologies." ,
    Application_Based="Real-world scenarios that apply concepts practically."
 
LLM_models={
    "OpenAI":"gpt-4o",
    'Anthropic':"claude-3-sonnet-20240229",
    "Google AI Studio":"gemini/gemini-1.5-flash"
}
