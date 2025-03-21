import streamlit as st
from tempfile import NamedTemporaryFile
from ollama import chat
import json
from langchain_community.document_loaders import (
    TextLoader, PyPDFLoader, YoutubeLoader, WebBaseLoader,Docx2txtLoader
)
from utils import *

loaders={
        "txt":TextLoader,
        "pdf":PyPDFLoader,
        "docx":Docx2txtLoader, 
        "doc":Docx2txtLoader
    }  

def save_sources(files):
    """
    Saves uploaded files, reads their content using appropriate loaders,
    displays the content in the app, and saves the content to the database.
    """
    try:
        for file in files:
            file_type=file.name.split(".")[-1]
            with NamedTemporaryFile(delete=False, suffix=f".{file_type}") as temp_file:
                temp_file.write(file.read())
            loader = loaders.get(file_type)
            document=loader(temp_file.name).load()
            st.title(file.name)
            for docs in document:
                st.write(docs.page_content)
                save_to_database(file.name,docs.page_content)
        st.success("Files sucessfuly loaded")
    except Exception as e:
        st.write(e)
        st.warning("Unsupported file format")
        
def upload_file():
    """
    Creates a file uploader in the sidebar using Streamlit.
    Allows users to upload multiple files of specified types (txt, pdf, docx).
    When the 'Load Sources' button is pressed, it calls the save_sources function
    to process and save the uploaded files.
    """
    files = st.file_uploader("Upload files", accept_multiple_files=True,type=["txt", "pdf", "docx"])
    if st.button("Load Sources"):
        save_sources(files)

def show_titles_and_pages(contents):
    """
    Displays document titles in the sidebar using an expander.
    Allows users to select a document title and view its content page by page.
    Also displays the total length of the content in the sidebar.
    """
    total_length = sum(len(content) for content in contents)
    with st.sidebar.expander("Pages"): 
        page_num=st.selectbox("Page Number",range(len(contents)))
        st.write(contents[page_num])
    st.divider()
    st.sidebar.write(total_length)

def parse_quiz(quizlist):
    """
    Parses the quiz data from a Quizlist object into a list of dictionaries.
    Each dictionary represents a quiz question and contains the question,
    choices, correct answer, and explanation.
    """
    parsed_data = []
    for quiz in quizlist.quizzes:  # Access the 'quizzes' attribute
        parsed_data.append({
            "question": quiz.question,
             "choices": quiz.choices,
            "correct_answer": quiz.correct_answer,
           "explanation": quiz.explanation
         })
    return parsed_data

def show_quiz(parsed_quiz):
    """
    Displays the quiz questions and answer choices using Streamlit.
    Handles quiz state using Streamlit session state to track the current question,
    user's answer, and quiz completion. Provides feedback on answer submission
    and navigation between questions.
    """
    if "counter" not in st.session_state:
        st.session_state.counter = 0
    if "correct_answer_counter" not in st.session_state:
        st.session_state.correct_answer_counter = 0  # Track correct answers
    
    if "answered" not in st.session_state:
        st.session_state.answered = False  # Track if the current question was answered

    # Stop the quiz if all questions are answered
    if st.session_state.counter >= len(parsed_quiz):
        st.success("Quiz Completed! 🎉")
        grade_quiz(st.session_state.correct_answer_counter, len(parsed_quiz))
        # show_download_button(parsed_quiz) # Show download button after quiz completion
        return
    
    # Get current question
    quiz_item = parsed_quiz[st.session_state.counter]
    question = quiz_item["question"]
    choices = quiz_item["choices"]
    correct_answer = quiz_item["correct_answer"]
    explanation = quiz_item["explanation"]

    # Display question and choices
    answer = st.radio(question, choices, index=None, key=st.session_state.counter)

    col1, col2 = st.columns(2)

    # Submit button logic
    if col1.button("Submit") and not st.session_state.answered:
        if answer:
            if answer == correct_answer:
                st.session_state.correct_answer_counter += 1
                st.success("Good Job, you are correct ✅")
            else:
                st.warning("Sorry, you got it wrong 🚨")

            # Show explanation
            with st.expander("See explanation"):
                st.write(explanation)

            # Mark question as answered
            st.session_state.answered = True
        else:
            st.warning("Please choose an option before submitting!")

    # Next button logic (Prevent skipping unanswered questions)
    if col2.button("Next"):
        if not st.session_state.answered:
            st.warning("You must submit an answer before proceeding to the next question!")
        else:
            st.session_state.counter += 1
            st.session_state.answered = False  # Reset for next question
            st.rerun()  # Refresh to load next question

def grade_quiz(correct_answers, total_questions):
    """
    Displays the quiz grade to the user, showing the number of correct answers
    out of the total number of questions.
    """
    st.write(f"### You got **{correct_answers}** correct answers out of **{total_questions}** questions! 🎉")
    
def show_download_button(parsed_quiz):
    pdf_file = save_pdf(parsed_quiz)  # creates the pdf and returns the file path
    with open(pdf_file, "rb") as file:
        st.download_button(
            label="Download Quiz PDF",
            data=file,
            file_name="quiz.pdf",
            mime="application/pdf",
            )

def main():
    """
    Main function to run the Streamlit QuizGenerator app.
    Sets up the header, sidebar, document selection, content display,
    quiz generation, and quiz display functionalities.
    """
    st.header("QuizGenerator App")

    with st.sidebar:
        st.write("My first Streamlit app")
        upload_file()
        titles = get_titles()

    selected_title = st.selectbox("Selected Documents", titles, key="selected_title")
    contents = get_content(selected_title)
    show_titles_and_pages(contents)
    prompt = reduced_prompt(contents)

    num_question = st.slider("How many questions would you like to generate?", 1, 20)  # Min 1 question
    st.write(f"You have chosen {num_question} questions.")

    if st.button("Generate Quiz"):
        if num_question > 0:  # Prevent 0-question quiz
            quiz = generate_quiz(prompt, num_question)
            st.session_state.parsed_quiz = parse_quiz(quiz)  # Store parsed quiz
            st.session_state.quiz_started = True  # Track quiz state
            # st.rerun()
        else:
            st.warning("Please select at least 1 question.")
       
    # Display quiz if it has been generated
    if st.session_state.get("quiz_started", False):
        parsed_quiz = st.session_state.parsed_quiz # Get parsed quiz from session state
        show_quiz(parsed_quiz)  # Show the parsed quiz
        show_download_button(parsed_quiz) # Show download button after quiz is shown

if __name__=="__main__":
    main()
