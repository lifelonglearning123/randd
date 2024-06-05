from openai import OpenAI

# Set your OpenAI Assistant ID here
assistant_id = 'asst_ct2tGsfN0xrDG3RzTCaeoa6M'

openai = OpenAI(default_headers={"OpenAI-Beta": "assistants=v1"})
# Initialize the OpenAI client (ensure to set your API key in the sidebar within the app)
openai.api_key = config("OPENAI_API_KEY")  # Use config to get the API key

if "openai_model" not in st.session_state:
    st.session_state.openai_model = "gpt-4-turbo"
    
    
