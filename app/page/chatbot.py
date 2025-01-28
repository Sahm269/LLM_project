import streamlit as st



st.markdown(
    """
    <style>
        .title-container {
            background-color: #FF9A76;
            border-radius: 10px;
            color: white;
            text-align: center;
            padding: 5px;
            margin-bottom: 20px;
            box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
            font-family: New Icon;
            font-size: 25px;
        }

        .chat {
            position: relative;
            height: 430px;
            padding: 20px;
        }

        .chat h3{
            font-size: 26px;
            color: #ff8266;
            font-weight: bold;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
        }

        .chat p {
            font-size: 18px;
            color: #555;
            margin-top: 0;
        }

        .history {
            background-color: #e6e6e6;
            color: black;
            height: 410px;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 4px 4px 6px rgba(0, 0, 0, 0.1);
            font-family: 'Roboto', sans-serif;
            color: white;
        }

        .history h4 {
            font-size: 24px;
            font-weight: bold;
            color: #ff8266;
            text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.2);
        }

        .button-container {
            display: flex;
            justify-content: center;
            margin: 20px;
        }

        .custom-button {
            background-color: #66cc66;
            color: white;
            border: none;
            border-radius: 10px;
            padding: 10px 20px;
            font-size: 18px;
            cursor: pointer;
            box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
            transition: background-color 0.3s;
            width: 100%;
        }

        .custom-button:hover {
            background-color: #39ac39;
        }   

        .stTextInput input {
            background-color: #d9d9d9;
            border-radius: 10px;
            padding: 10px;
            font-size: 16px;
            width: 100%;
            outline: none;
        }

        .stTextInput input:focus {
            border-color: #ff9a76;
            box-shadow: 0 0 5px rgba(255, 154, 118, 0.5);
        }

        .stButton button {
            background-color: #d9d9d9;
            color: white;
            border: none;
            border-radius: 10px;
            padding: 10px 20px;
            font-size: 18px;
            cursor: pointer;
            box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
            transition: background-color 0.3s;
        }

        .stButton button:hover {
            background-color: #bfbfbf;
        }

        .chat-input-container {
            position: absolute;
            width: 100%;
        }

        .chat-input-container .stTextInput,
        .chat-input-container .stButton {
            margin: 3px 0;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="title-container">
        CHATBOT
    </div>
    """,
    unsafe_allow_html=True,
)

col1, col2 = st.columns([3, 2])

with col1:
    st.markdown(
        """
        <div class="column chat">
            <h3>Bienvenue dans la zone de chat! 🤖</h3>
            <p>Posez votre question 💬</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1a, col1b = st.columns([5, 1])

    with col1a:
        user_input = st.text_input("", placeholder="Tapez votre message ici", key="user_input", max_chars=200)
        
    with col1b:
        st.markdown("<br>", unsafe_allow_html=True)
        st.button("📤", key="send_button")

with col2:


    


    st.markdown(
        """
        <div class="column history">
            <h4>📚 Historique</h4>
        </div>
        """,
        unsafe_allow_html=True,
    )