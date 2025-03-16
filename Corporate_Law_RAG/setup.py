import streamlit as st

# service parameters
CORTEX_SEARCH_DATABASE = "STREAMLIT_APP"
CORTEX_SEARCH_SCHEMA = "DATA_SCHEMA"
CORTEX_SEARCH_SERVICE= "LEGAL_CHECKER"
######

def get_parameters(account, user, password,role="ACCOUNTADMIN",database=CORTEX_SEARCH_DATABASE
                   ,warehouse="COMPUTE_WH",schema=CORTEX_SEARCH_SCHEMA):
    CONNECTION_PARAMETERS = {
        "account": account,
        "user": user,
        "password": password,
        "role": role,
        "database":database,
        "warehouse": warehouse,
        "schema": schema,
    }
    return CONNECTION_PARAMETERS


def config_options():
    st.sidebar.selectbox('Select your model:',('mistral-large2', 'llama3.1-70b',
                                    'llama3.1-8b', 'snowflake-arctic'), key="model_name")

    conn = st.session_state.connector
    cursor = conn.cursor()
    try:
        cursor.execute(f"SELECT DISTINCT category FROM chunks_table") # Fetch distinct categories using SQL
        categories = cursor.fetchall()
        cat_list = ['ALL']
        for cat in categories:
            cat_list.append(cat[0])  # Assuming category is the first column
    except Exception as e:
        st.error(f"Error fetching categories: {e}")
        cat_list = ['ALL', 'Error fetching categories'] # Provide default options in case of error
    finally:
        cursor.close()

    st.sidebar.selectbox('Select what aspect of company law you\'re looking for', cat_list, key = "category_value")

    # st.sidebar.checkbox('Do you want that I remember the chat history?', key="use_chat_history", value = True)

    st.sidebar.checkbox('Debug: Click to see summary generated of previous conversation', key="debug", value = True)
    st.sidebar.button("Start Over", key="clear_conversation", on_click=init_messages)
    # st.sidebar.expander("Session State").write(st.session_state)

def init_messages():
    # Initialize chat history
    if st.session_state.clear_conversation or "messages" not in st.session_state:
        st.session_state.messages = []
