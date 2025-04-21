# from ollama import chat
import streamlit as st
from utils import save_pdf

def display_quiz(parsed_quiz):
    """
    Displays the quiz questions and answer choices using Streamlit.
    Handles quiz state using Streamlit session state to track the current question,
    user's answer, and quiz completion. 
    Provides feedback on answer submission and navigation between questions.
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
        st.session_state.counter=0
        st.session_state.correct_answer_counter = 0  
        # show_download_button(parsed_quiz) # Show download button after quiz completion
        return
    
    # Get current question
    quiz_item = parsed_quiz[st.session_state.counter]
    question = quiz_item["question"]
    choices = quiz_item["choices"]
    correct_answer = quiz_item["correct_answer"]
    explanation = quiz_item["explanation"]

    # Display question and choices
    ques_num=str(st.session_state.counter+1)
    st.markdown(f"##### :gray[{ques_num}]. {question}") 
    answer = st.radio(" ", choices, index=None, key=st.session_state.counter)

    col1, col2 = st.columns(2)
    if col1.button("Submit") and not st.session_state.answered:
        submit(answer,correct_answer,explanation)
     # Next button logic (Prevent skipping unanswered questions)
    if col2.button("Next"):
        if not st.session_state.answered:
            st.warning("You must submit an answer before proceeding to the next question!")
        else:
            st.session_state.counter += 1
            st.session_state.answered = False  # Reset for next question
            st.rerun()  # Refresh to load next question


def submit(answer,correct_answer,explanation):
    # Submit button logic
    if answer:
        if answer == correct_answer:
            st.session_state.correct_answer_counter += 1
            st.success("Good Job, you are correct ✅")
        else:
            st.warning("Sorry, you got it wrong 🚨")

        # Show explanation
        with st.expander("See explanation"):
            st.subheader(f"Answer: {correct_answer}", divider="gray")
            st.write(explanation)

        # Mark question as answered
        st.session_state.answered = True
    else:
        st.warning("Please choose an option before submitting!")


def grade_quiz(correct_answers, total_questions):
    """
    Displays the quiz grade to the user, showing the number of correct answers
    out of the total number of questions.
    """
    st.write(f"### You got **{correct_answers}** correct answers out of **{total_questions}** questions! 🎉")


def show_download_button(parsed_quiz):
    pdf_file = save_pdf(parsed_quiz)  # creates the pdf and returns the file path
    title=st.session_state.selected_title
    with open(pdf_file, "rb") as file:
        st.download_button(
            label="Download Quiz PDF",
            data=file,
            file_name = f"{title[:10] if len(title) > 10 else title} quiz.pdf",
            mime="application/pdf",
            )


