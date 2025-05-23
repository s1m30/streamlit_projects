from bs4 import BeautifulSoup as bsoup
from langchain_community.document_loaders import (
    TextLoader, PyPDFLoader, WebBaseLoader,Docx2txtLoader
)
import os
from langchain_text_splitters import RecursiveCharacterTextSplitter as splitter
import streamlit as st
from tempfile import NamedTemporaryFile
import requests

loaders={
        "txt":TextLoader,
        "pdf":PyPDFLoader,
        "docx":Docx2txtLoader, 
        "doc":Docx2txtLoader,
        "web":WebBaseLoader,
    }  

class Loader():
    def __init__(self,files,web:str):
        self.files=files
        self.web=web
    
    def is_valid_website(self,website):
        response = requests.get(website)
        if response.status_code == 200:
            soup = bsoup(response.content, 'html.parser')
            title_tag = soup.find('title')
            # Parse the webpage content
            soup =bsoup(response.text, 'html.parser')

            # Extract the title from the HTML
            title_tag = soup.find("title")
            title = title_tag.text if title_tag else "No Title Found"
            return title
        else:
            return None
    

    def load_sources(self):
        """
        Saves uploaded files, reads their content using appropriate loaders,
        displays the content in the app, and saves the content to the database.
        """
        try:
            sources = []
            if self.files:
                sources.extend(self.files)
            if self.web:
                sources.append(self.web)

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
                    title=self.is_valid_website(source)
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
                self.save_sources(contents,name)
            st.success("Loading Completed")
        except Exception as e:
            st.write(e)
            st.warning("Unsupported file format")


    def save_sources(self,contents,name):
        if contents:
            chunks=splitter( chunk_size=6500,chunk_overlap=30,).split_text(contents)
            self.save_to_dict(name,chunks)
            #For personal use on your local computer 
            # for chunk in chunks:
            #     save_to_database(name,chunk)
        else:
            st.warning(f"Unable to Extract Contents from {name}")
      
        
    def save_to_dict(self,title,content):
        st.session_state.documents[title]=content


    # Uncomment if you wish to use the Sqlite3 db on your Pc instead
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
        
