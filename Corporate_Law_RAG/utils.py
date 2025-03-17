from snowflake.cortex import complete
import streamlit as st
from snowflake.core import Root # requires snowflake>=0.8.0
from session import SESSION,SVC
CORTEX_SEARCH_DATABASE = "STREAMLIT_APP"
CORTEX_SEARCH_SCHEMA = "DATA_SCHEMA"
CORTEX_SEARCH_SERVICE= "LEGAL_CHECKER"
### Default Values
NUM_CHUNKS = 5# Num-chunks provided as context. Play with this to check how it affects your accuracy
slide_window = 7 # how many last conversations to remember. This is the slide window.

# columns to query in the service
COLUMNS = [
    "chunk",
    "category"]


#Describe Prompt
def create_prompt (myquestion):
    
    chat_history = get_chat_history()
    if chat_history != []: #There is chat_history, so not first question
        question_summary = summarize_question_with_history(chat_history, myquestion)
        prompt_context =  get_similar_chunks_search_service(question_summary)
    else:
        prompt_context = get_similar_chunks_search_service(myquestion) #First question when using history
  
    prompt = f"""
           You are an expert company law advisor that extracts information from the CONTEXT on Nigerian company law 
           provided between <context> and </context> tags to help the user.
           You offer a chat experience considering the information included in the CHAT HISTORY
           provided between <chat_history> and </chat_history> tags..
           When ansering the question contained between <question> and </question> tags
           be concise and do not hallucinate. 
           Do not mention the CONTEXT used in your answer.
           Do not mention the CHAT HISTORY used in your asnwer.

           Only answer the question if you can extract it from the CONTEXT provideed.
           
           <chat_history>
           {chat_history}
           </chat_history>
           <context>          
           {prompt_context}
           </context>
           <question>  
           {myquestion}
           </question>
           Answer: 
           """
    return prompt


def answer_question(myquestion):
    prompt =create_prompt (myquestion)
    response = complete(model=st.session_state.model_name, prompt=prompt,session=SESSION)
    return response


def get_similar_chunks_search_service(query):
    if st.session_state.category_value == "ALL":
        response = SVC.search(query, COLUMNS, limit=NUM_CHUNKS)
    elif st.session_state.category_value != "ALL":
        filter_obj = {"@eq": {"category": st.session_state.category_value} }
        response = SVC.search(query, COLUMNS, filter=filter_obj, limit=NUM_CHUNKS)
    # st.sidebar.json(response.json())
    return response.json()


#Get the history from the st.session_stage.messages according to the slide window parameter
def get_chat_history():
    chat_history = []
    start_index = max(0, len(st.session_state.messages) - slide_window)
    for i in range (start_index , len(st.session_state.messages) -1):
         chat_history.append(st.session_state.messages[i])

    return chat_history

# To get the right context, use the LLM to first summarize the previous conversation
# This will be used to get embeddings and find similar chunks in the docs for context
def summarize_question_with_history(chat_history, question):
    prompt = f"""
        Based on the chat history below and the question, generate a query that extend the question
        with the chat history provided. The query should be in natual language. 
        Answer with only the query. Do not add any explanation.
        
        <chat_history>
        {str(chat_history)}
        </chat_history>
        <question>
        {question}
        </question>
        """
    print("This is the prompt",prompt)
    summary = complete(st.session_state.model_name, prompt,session=SESSION)   
    summary = summary.replace("'", "")
    return summary
