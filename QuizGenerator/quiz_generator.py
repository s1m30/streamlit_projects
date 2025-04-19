from litellm import completion, check_valid_key
from pydantic import BaseModel
import streamlit as st

#Defines Pydantic models for quiz generation
class Quiz(BaseModel):
    question: str
    choices: list[str]
    correct_answer: str
    explanation:str

class Quizlist(BaseModel):
    quizzes:list[Quiz]

class Quizgenerator(): 
    def __init__(self,content,num,style,style_desc):
        self.content=content
        self.num=num
        self.style=style
        self.style_desc=style_desc

    def generate_quiz(self):
        """
        Generates a multiple-choice quiz using the Ollama language model.
        Arguments:
        - content_text: The content from which to generate the quiz.
        - question_num: The number of questions to generate.
        Returns a list of Quiz objects.
        """

        content_text=self.content
        question_num=self.num
        question_style=self.style
        question_style_desc=self.style_desc
        st.session_state.counter=0
        
        SYSTEM_PROMPT= f"""#Instruction
                            You are a professor. Using the provided lecture content, create a Master-level multiple-choice exam in strict JSON format that includes exactly {question_num} questions. 
                            Ensure the structure is:
                            [{{'question': '...', 'choices': ['...'], 'correct_answer': '...', 'explanation': '...'}}, ...]\n
                            
                            #Further Instructions
                            -Your question style must be {question_style}: {question_style_desc}
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
        api_key=st.session_state.api_key
        model_name=st.session_state.model_name
            
        try:
            response = completion(
                api_key=api_key,
                model=model_name,
                response_format=Quizlist,
                messages=[{'role': 'system', 'content': SYSTEM_PROMPT},
                        {'role': 'user', 'content': f"#Content: {content_text}"}],
            )
        except Exception as e:
            print(f"Error during API call: {e}")
            return f"An error occurred while calling the API. Please check your API key and provider."

        # Extract response content (which should be a JSON string)
        try:
            quiz_obj = Quizlist.model_validate_json(response.choices[0].message.content)
            return self.parse_quiz(quiz_obj)
        except Exception as e:
            print("Error parsing response:", e)
            return "Error parsing the quiz response."
    
    def parse_quiz(self, quizlist:Quizlist):
        """
        Parses the quiz data from a Quizlist object into a list of dictionaries.
        Each dictionary represents a quiz question and contains the question,
        choices, correct answer, and explanation.
        """
        parsed_data = []
        if quizlist and hasattr(quizlist, 'quizzes'):  # Ensure quizlist is valid and has 'quizzes'
            for quiz in quizlist.quizzes:  # Access the 'quizzes' attribute
                parsed_data.append({
                    "question": quiz.question,
                    "choices": quiz.choices,
                    "correct_answer": quiz.correct_answer,
                    "explanation": quiz.explanation
                })
        return parsed_data
