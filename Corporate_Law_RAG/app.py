import streamlit as st
from setup import config_options, init_messages
from utils import answer_question
from setup import get_parameters
import snowflake.connector

if 'connector' not in st.session_state:
    st.session_state.connector = snowflake.connector.connect(**get_parameters(st.secrets["ACCOUNT"],st.secrets["USER"],st.secrets["PASSWORD"]))
 
def main():
    # Ensure credentials are stored in st.session_state
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
