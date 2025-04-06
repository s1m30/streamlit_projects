# from ollama import chat
from pydantic import BaseModel
import streamlit as st
from utils import save_pdf
from litellm import completion

#Defines Pydantic models for quiz generation
class Quiz(BaseModel):
    question: str
    choices: list[str]
    correct_answer: str
    explanation:str
class Quizlist(BaseModel):
    quizzes:list[Quiz]
    

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


def generate_quiz(content_text, question_num,question_style=None):
    """
    Generates a multiple-choice quiz using the Ollama language model.
    Arguments:
    - content_text: The content from which to generate the quiz.
    - question_num: The number of questions to generate.
    Returns a list of Quiz objects.
    """
    
    SYSTEM_PROMPT= f"""#Instruction
                        You are a professor. Using the provided lecture content, create a Master-level multiple-choice exam in strict JSON format that includes exactly {question_num} questions. 
                        Ensure the structure is:
                        [{{'question': '...', 'choices': ['...'], 'correct_answer': '...', 'explanation': '...'}}, ...]\n
                        
                        #Further Instructions
                        -Your question style should be {question_style if question_style!=None else "optimal based on the nature of the content"} 
                        -The questions should be challenging and require critical thinking.
                        -Avoid excessive whitespaces
                        -Always return output as JSON format
                    """
    
    #Using Ollama                  
    # response = chat(
    # messages=[{'role': 'system','content': SYSTEM_PROMPT},
    #           {'role':'user','content':f"#Content: {content_text}"}],
    # model='llama3',
    # format=Quizlist.model_json_schema(),
    # )
    
    #Using Litellm
    response = completion(
    api_key="",
    model="gemini/gemini-1.5-flash",
    response_format=Quizlist,
    messages=[{'role': 'system','content': SYSTEM_PROMPT},
              {'role':'user','content':f"#Content: {content_text}"}],
    )

    # Extract response content (which should be a JSON string)
    try:
        # quiz_obj = Quizlist.model_validate_json(response.message.content) #Using Ollama
        quiz_obj=Quizlist.model_validate_json(response.choices[0].message.content) #Using Litellm
        return quiz_obj

    except Exception as e:
        print("Error parsing response:", e)
        return None


def show_download_button(parsed_quiz):
    pdf_file = save_pdf(parsed_quiz)  # creates the pdf and returns the file path
    with open(pdf_file, "rb") as file:
        st.download_button(
            label="Download Quiz PDF",
            data=file,
            file_name=f"{st.session_state.selected_title}",
            mime="application/pdf",
            )


