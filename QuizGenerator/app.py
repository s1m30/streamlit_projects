import streamlit as st
from utils import get_titles, get_content,show_titles_and_pages
from quiz_utils import *
from loaders import upload_file

style_options=[
    "Factual",
    "Mathematical",
    "Coding/Programming",
    "Case-Study Based",
    "Conceptual",
    "Theoretical",
    "Technical",
    "Application-Based"
]
    
    
def main():
    """
    Main function to run the Streamlit QuizGenerator app.
    Sets up the header, sidebar, document selection, content display,
    quiz generation, and quiz display functionalities.
    """
    st.header("QuizGenerator App")

    with st.sidebar:
        upload_file()
        titles = get_titles()

    selected_title = st.selectbox("Selected Documents", titles, key="selected_title")
    # st.selectbox("Choose a section")
    contents = get_content(selected_title)
    show_titles_and_pages(contents) # Display document titles and pages
    num_question = st.slider("How many questions would you like to generate?", 5, 25)  # Min 1 question
    st.write(f"You have chosen {num_question} questions.")
    style_option=st.selectbox("Choose Question Style", style_options)

    
    if st.button("Generate Quiz"):
        if num_question > 0:  # Prevent 0-question quiz
            quiz = generate_quiz(contents[st.session_state.page_num], num_question, style_option)
            st.session_state.parsed_quiz = parse_quiz(quiz)  # Store parsed quiz
            st.session_state.quiz_started = True  # Track quiz state
            # st.rerun()
        else:
            st.warning("Please select at least 1 question.")
       
    # Display quiz if it has been generated
    if st.session_state.get("quiz_started", False):
        parsed_quiz = st.session_state.parsed_quiz # Get parsed quiz from session state
        display_quiz(parsed_quiz)  # Show the parsed quiz
        show_download_button(parsed_quiz) # Show download button after quiz is shown

if __name__=="__main__":
    main()
