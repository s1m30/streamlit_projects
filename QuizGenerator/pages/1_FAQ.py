import streamlit as st 

st.set_page_config(
    page_title="FAQ",
    page_icon="❓"
)

st.markdown(
    "<style>#MainMenu{visibility:hidden;}</style>",
    unsafe_allow_html=True
)

st.title("❓ FAQ (Frequently Asked Questions)")
st.write("💬 **Have a question about Iquill?** You're in the right place!")

with st.expander("👥 Who can use Iquill?", expanded=True):
    st.markdown(
        "Anyone! 👩‍🏫👨‍🎓 Iquill is built for **students**, **teachers**, **self-learners**, or anyone who wants to quickly generate quizzes for learning, teaching, or testing purposes."
    )

with st.expander("🚀 Why Iquill?"):
    st.markdown(
        "Because creating quizzes shouldn't be a chore! 🛠️\n\n"
        "Iquill is designed to make quiz creation **fast**, **simple**, and **efficient**—so you can focus on **learning or teaching**, not formatting questions."
    )

with st.expander("✨ What features are available?"):
    st.markdown(
        "Iquill offers all the essentials to streamline your quiz experience:\n\n"
        "- 🎨 **Choose your question style**\n"
        "- 📝 **Take quizzes directly in-app**\n"
        "- 📥 **Download quizzes with answers**\n"
        "- 🧠 **AI-generated content**\n"
        "- 🌐 **Support for websites & document uploads**"
    )

with st.expander("🛠️ How can I generate my quiz?"):
    st.markdown(
        "Just follow these simple steps:\n\n"
        "1. 📄 Upload a document (**PDF**, **TXT**, or **DOCX**) or paste a website link.\n"
        "2. 🔑 Provide your API key (see below).\n"
        "3. 🧠 Let Iquill generate your quiz!\n"
        "It’s that easy!"
    )

with st.expander("🔐 Why do I need an API key?"):
    st.markdown(
        "An API key connects you to the AI model that powers your quiz. 🧠\n\n"
        "Without it, Iquill can't generate questions for you."
    )

with st.expander("🔑 How can I get an API key?"):
    st.markdown(
        "You can get one based on your preferred AI provider:\n\n"
        "- 💡 [Google AI Studio](https://aistudio.google.com/) — *Recommended & free!*\n"
        "- 🤖 OpenAI\n"
        "- 🧬 Anthropic\n\n"
        "Once you have a key, paste it into the sidebar."
    )

with st.expander("⚠️ Why am I seeing the error 'The API key appears to be invalid. Please double-check it'?"):
    st.markdown(
        "This usually means:\n\n"
        "- 🚫 Your API key is incorrect\n"
        "- 🔁 You've hit your usage limit\n"
        "- 💰 You've exceeded your monthly spending cap\n\n"
        "Double-check your API dashboard for more info."
    )

with st.expander("🔒 Is my information kept confidential on Iquill?"):
    st.markdown(
        "Absolutely! ✅ Your documents are **never stored**.\n\n"
        "We value your **privacy** and **data security** above all. 🔐"
    )
