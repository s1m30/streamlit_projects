import streamlit as st
from main import main
if __name__=="__main__":
    st.set_page_config(
    page_title="IQuill",
    page_icon="✍️",
    initial_sidebar_state="expanded"
)  
    st.header("The **Quill**🤖 invites you to take a **quiz**✨📘")
        
    # Add this line just below the divider
    st.markdown(
        "💡 **Having trouble getting started?** Visit the [FAQ](./FAQ) for help 👈.",
        unsafe_allow_html=True
    )
    st.divider()

    main()
