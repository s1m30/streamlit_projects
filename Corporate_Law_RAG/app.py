import streamlit as st
from setup import config_options, init_messages
from utils import answer_question
def main():
    st.title(f":speech_balloon: Nigerian Company law with Snowflake Cortex")
    st.write("Leverage our FREE Company Legal advisor to your benefit. You can find the main source at https://natlex.ilo.org/dyn/natlex2/natlex2/files/download/112593/NGA112593.pdf")
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
