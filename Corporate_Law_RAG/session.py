import os
from snowflake.snowpark import Session
from snowflake.core import Root
from setup import get_parameters
import streamlit as st
CORTEX_SEARCH_DATABASE = "STREAMLIT_APP"
CORTEX_SEARCH_SCHEMA = "DATA_SCHEMA"
CORTEX_SEARCH_SERVICE= "LEGAL_CHECKER"

SESSION = Session.builder.configs(get_parameters(st.secrets["ACCOUNT"],st.secrets["USER"],st.secrets["PASSWORD"])).create()
SVC = Root(SESSION).databases[CORTEX_SEARCH_DATABASE].schemas[CORTEX_SEARCH_SCHEMA].cortex_search_services[CORTEX_SEARCH_SERVICE]
