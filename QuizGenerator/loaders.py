import sqlite3
from langchain_community.document_loaders import (
    TextLoader, PyPDFLoader, WebBaseLoader,Docx2txtLoader
)
import os
from langchain_text_splitters import RecursiveCharacterTextSplitter as splitter
import streamlit as st
from tempfile import NamedTemporaryFile
from utils import *



loaders={
        "txt":TextLoader,
        "pdf":PyPDFLoader,
        "docx":Docx2txtLoader, 
        "doc":Docx2txtLoader,
        "web":WebBaseLoader,
    }  


def save_sources(files,web:str):
    """
    Saves uploaded files, reads their content using appropriate loaders,
    displays the content in the app, and saves the content to the database.
    """
    try:
        sources = []
        if files:
            sources.extend(files)
        if web:
            sources.append(web)

        for source in sources:
            file_type = None
            name = None
            
            if hasattr(source, 'name') and hasattr(source, 'read'):
                file_type=source.name.split(".")[-1]
                with NamedTemporaryFile(delete=False, suffix=f".{file_type}") as temp_file:
                    temp_file.write(source.read())
                    name=os.path.splitext(source.name)[0]
                    source=temp_file.name
                    
            elif isinstance(source,str):
                title=is_valid_website(source)
                if title:
                    file_type="web"
                    name=title
                else:
                    st.warning(f"Unsupported source: {source}")
                    continue # Skip to the next source if not recognized
            
            loader = loaders.get(file_type)
            document=loader(source).load()
            content_list=[]
            for docs in document:
                content_list.append(docs.page_content)
            contents="".join(content_list)
            chunks=splitter( chunk_size=6500,chunk_overlap=30,).split_text(contents)
            #For personal use on your local computer 
            # for chunk in chunks:
            #     save_to_database(name,chunk)
            save_to_dict(name,chunks)

        st.success("Files sucessfuly loaded")
    except Exception as e:
        st.write(e)
        st.warning("Unsupported file format")


def upload_file():
    """
    Creates a file uploader in the sidebar using Streamlit.
    Allows users to upload multiple files of specified types (txt, pdf, docx).
    When the 'Load Sources' button is pressed, it calls the save_sources function
    to process and save the uploaded files.
    """
    files = st.file_uploader("Upload files", accept_multiple_files=True,type=["txt", "pdf", "docx"])
    web=st.text_input("Input a website source")
    if st.button("Load Sources"):
        with st.spinner("The Quill is taking a look"):
            save_sources(files,web)

# Uncomment if you wish to use the Sqlite3 db on your Pc
# def save_to_database(title, content):
#     """
#     Saves document title and content to an SQLite database.
#     Initializes the database and table if they don't exist.
#     """
#     # # Connect to an SQLite database (or create it if it doesn't exist)
#     conn = sqlite3.connect('content.db')
#     # # Create a cursor object using the cursor() method
#     cursor = conn.cursor()
#     # # Create table
#     cursor.execute('''CREATE TABLE IF NOT EXISTS documents
#                   (title text, content text)''')
#     # # Insert a row of data
#     cursor.execute("INSERT INTO documents (title,content) VALUES (?, ?)", (title, content))
#     # # Save (commit) the changes
#     conn.commit()
#     # # Close the connection
#     conn.close()

def save_to_dict(title,content):
    st.session_state.documents[title]=content
    
