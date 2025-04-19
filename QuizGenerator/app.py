import streamlit as st
from utils import *
from quiz_utils import *
from quiz_generator import Quizgenerator
from litellm import check_valid_key

def main():
    """
    Main function to run the Streamlit QuizGenerator app.
    Sets up the header, sidebar, document selection, content display,
    quiz generation, and quiz display functionalities.
    """
    if not "documents" in st.session_state:
        st.session_state.documents={}

    st.header("The **Quill**🤖 invites you to take a **quiz**✨📘")
    st.divider()
    
    # Sidebar or main input for API provider and key
    with st.sidebar:
        st.title("🔑 API Settings")
        provider = st.selectbox("Select AI Provider", ["OpenAI", "Google AI Studio", "Anthropic"], key="providers", 
                                help="You can get a free API key from Google AI Studio at https://aistudio.google.com/")
        api_key = st.text_input(f"Enter your {provider} API Key",key="api_key", type="password")
        st.divider()
        upload_file()
        
    titles = get_titles()
    selected_title = st.selectbox("Selected Documents", titles, key="selected_title")
    style_options= [style.name.replace("_", " ") for style in StyleOptions]
    style_option=st.selectbox("Choose Question Style", style_options)
    style_desc=StyleOptions[style_option.replace(" ", "_")].value
    # st.sidebar.json(st.session_state)

    if selected_title: 
        # st.selectbox("Choose a section")
        contents = get_content(selected_title)
        show_titles_and_pages(contents) # Display document titles and pages
        num_question = st.slider("How many questions would you like to generate?", 5, 25)  # Min 1 question
        st.write(f"You have chosen {num_question} questions.")
        st.divider()

        if st.button("Generate Quiz"):
            if api_key:
                #Defines model providers
                st.session_state.model_name=LLM_models.get(st.session_state.providers)
                is_valid_key = check_valid_key(model=st.session_state.model_name, api_key=api_key)
                if not is_valid_key:
                    st.warning(f"The API key for {st.session_state.providers} appears to be invalid. Please double-check it.")
                else:
                    with st.spinner("Your quiz is being generated"):
                        quiz_gen_obj=Quizgenerator(contents[st.session_state.page_num], num_question, style_option,style_desc)
                        st.session_state.parsed_quiz = quiz_gen_obj.generate_quiz() #Store Parsed Quiz
                        st.session_state.quiz_started = True  # Track quiz state
            elif not api_key:
                st.warning("Please enter your API key.")
       

        # Display quiz if it has been generated
        if st.session_state.get("quiz_started", False):
            with st.container(border=True):
                parsed_quiz = st.session_state.parsed_quiz # Get parsed quiz from session state
                display_quiz(parsed_quiz)  # Show the parsed quiz
            show_download_button(parsed_quiz) # Show download button after quiz is shown

if __name__=="__main__":
    st.set_page_config(
    page_title="IQuill",
    page_icon="🤖",
    initial_sidebar_state="expanded"
)
    main()
