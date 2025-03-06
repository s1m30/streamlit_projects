import streamlit as st
from setup import config_options, init_messages
from snowflake.snowpark import Session
from snowflake.core import Root # requires snowflake>=0.8.0
from setup import get_parameters
from snowflake.cortex import complete

CORTEX_SEARCH_DATABASE = "STREAMLIT_APP"
CORTEX_SEARCH_SCHEMA = "DATA_SCHEMA"
CORTEX_SEARCH_SERVICE= "LEGAL_CHECKER"
### Default Values
NUM_CHUNKS = 5# Num-chunks provided as context. Play with this to check how it affects your accuracy
slide_window = 7 # how many last conversations to remember. This is the slide window.
# Ensure credentials are stored in st.session_state and reuse session
if 'session' not in st.session_state:
    st.session_state.session = None
if 'root' not in st.session_state:
    st.session_state.root=None

st.session_state.session = Session.builder.configs(get_parameters(st.secrets["ACCOUNT"],st.secrets["USER"],st.secrets["PASSWORD"])).create()
st.session_state.root=Root(st.session_state.session)

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
    response = complete(model=st.session_state.model_name, prompt=prompt,session=st.session_state.session)
    return response


def get_similar_chunks_search_service(query):
    #Define Search Service 
    svc = st.session_state.root.databases[CORTEX_SEARCH_DATABASE].schemas[CORTEX_SEARCH_SCHEMA].cortex_search_services[CORTEX_SEARCH_SERVICE]
    if st.session_state.category_value == "ALL":
        response = svc.search(query, COLUMNS, limit=NUM_CHUNKS)
    elif st.session_state.category_value != "ALL":
        filter_obj = {"@eq": {"category": st.session_state.category_value} }
        response = svc.search(query, COLUMNS, filter=filter_obj, limit=NUM_CHUNKS)
    st.sidebar.json(response.json())
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
    summary = complete(st.session_state.model_name, prompt)   
    summary = summary.replace("'", "")
    return summary

def main():
    st.title("📚💡 Smart Company Law Advisor ")
    st.write(
        "Get instant insights on Nigerian company law with AI, based on the Companies and Allied Matters Act (CAMA) 2020. "
        "The main source is the CAMA 2020 Act, established by the Corporate Affairs Commission (CAC) to regulate corporate entities in Nigeria. "
    )
    st.link_button("CAMA 2020 Act", "https://natlex.ilo.org/dyn/natlex2/natlex2/files/download/112593/NGA112593.pdf")
    config_options()
    init_messages()

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if question := st.chat_input("What company law would you like to know about?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": question})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(question)
        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            message_placeholder = st.empty()

            question = question.replace("'","")

            with st.spinner(f"{st.session_state.model_name} thinking..."):
                response= answer_question(question)
                response = response.replace("'", "")
                message_placeholder.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})


if __name__ == "__main__":
    main()
