import streamlit as st
import json
import sys
sys.path.append(r'./')
import get_email
import gophish_api

# Set page title and layout
st.set_page_config(page_title="Phish Net Team", layout="wide", page_icon="🕸️")
with open('./streamlit/style.css') as f:
    css = f.read()

st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

st.markdown(
    """<style>

    .stForm {
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.3);
            margin: 15px
        }
    input[type="text"], selectbox, input[type="number"] {
            background-color: white;
            color: black;
            padding: 10px;
            border-radius: 5px;
        }
    input[type="text"]:focus, selectbox:focus, input[type="number"]:focus {
            outline: none;
            border-color: #58a6ff;
            box-shadow: 0 0 5px rgba(88, 166, 255, 0.8);
        }

    </style>
    """,
    unsafe_allow_html=True
)

# Sidebar content
with st.sidebar:
    # Add the logo
    st.image("./assets/phishnet_logo-modified.png", use_container_width=False)

    # About section
    st.markdown("""
    ## About the tool
    The Phish Net Team app demonstrates a phishing simulation using Generative AI and GoPhish.
    """)

    st.markdown("""
    ### How to use?""")
    st.write("1. Select the \"Single User Send\" or \"Bulk User Send\" tab.  \n 2. Fill in the employee details or upload a JSON file.  \n 3. Click on Send.  \n 4. Check Preview as the emails get generated.  \n 5. Review Campaign Statistics in the Gophish dashboard.")

# Main area content
st.header("Leverage the power of AI to send phishing emails.")
tab1, tab2= st.tabs(["Single User Send", "Bulk User Send"])

with tab1:
    st.markdown("""
    Enter the employee details.

    """)

    with st.form("employee_form"):
        employee = {}
        employee["FirstName"] = st.text_input("First Name")
        employee["LastName"] = st.text_input("Last Name")
        employee["Role"] = st.text_input("Role")
        employee["Email"] = st.text_input("Email")
        employee["PreferredLanguage"] = st.text_input("Preferred Language")
        employee["CarLease"] = st.text_input("Car Lease")
        employee["DependentCount"] = st.number_input("Number of Dependents", min_value=0, step=1)
        employee["Insurance"] = st.text_input("Insurance Provider")
        submitted = st.form_submit_button("Send Email")
        
        if submitted:
            as_list=[employee]
            with open("./assets/employee_details.json", "w", encoding="utf-8") as file:
                json.dump(as_list, file, indent=4, ensure_ascii=False)

            st.success("Generating email...")
            get_email.main("./assets/employee_details.json", "./assets/email.json")

            st.success("Email Generated!")
            st.subheader("Email Preview")
            
            with open("./assets/email.json", "r", encoding="utf-8") as file:
                emails= json.load(file)
            for email in emails:
                st.markdown(email["body"], unsafe_allow_html=True)
            
            st.success("Starting Email send..")
            gophish_api.main("./assets/email.json")

            st.success("Email Sent!")

with tab2:

# File uploader widget
    uploaded_file = st.file_uploader("Upload a JSON file", type=["json"])

    if uploaded_file is not None:
        try:
            # Read the uploaded JSON file
            json_data = json.load(uploaded_file)
            save_path = "from_streamlit.json" 
            with open(save_path, "w") as json_file:
                json.dump(json_data, json_file, indent=4)
                        
            st.success("File uploaded successfully!")
            st.success("Generating emails...")
            get_email.main("from_streamlit.json")

            st.success("Emails Generated!")
            st.subheader("Emails Preview")

            with open("./assets/emails.json", "r", encoding="utf-8") as file:
                emails= json.load(file)
            for email in emails:
                st.markdown(email["body"], unsafe_allow_html=True)
            
            st.success("Starting Email send..")
            #gophish_api.main()
            st.success("Emails Sent!")

                   
        except Exception as e:
            st.error(f"Error reading JSON file: {e}")
    else:
        st.info("Please upload a JSON file to proceed.")