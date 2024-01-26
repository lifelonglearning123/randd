# Import necessary libraries
import openai
import streamlit as st
import time
from decouple import config  # Import config from decouple


# Set your OpenAI Assistant ID here
assistant_id = 'asst_ct2tGsfN0xrDG3RzTCaeoa6M'


# Initialize the OpenAI client (ensure to set your API key in the sidebar within the app)
openai.api_key = config("OPENAI_API_KEY")  # Use config to get the API key

# Initialize session state variables for file IDs and chat control

if "thread_id" not in st.session_state:
    st.session_state.thread_id = None

if "file_id_list" not in st.session_state:
    st.session_state.file_id_list = []
# Set up the Streamlit page with a title and icon
st.set_page_config(page_title="ChatGPT-like Chat App", page_icon=":speech_balloon:")


# Function to associate files with the assistant
def associate_files_with_assistant(file_ids, assistant_id):
    for file_id in file_ids:
        openai.beta.assistants.files.create(
            assistant_id=assistant_id, 
            file_id=file_id
            
        )
        print(file_id)
        print(assistant_id)

# Define the function to process messages with citations
def process_message_with_citations(message):
    """Extract content and annotations from the message and format citations as footnotes."""
    message_content = message.content[0].text
    annotations = message_content.annotations if hasattr(message_content, 'annotations') else []
    citations = []

    # Iterate over the annotations and add footnotes
    for index, annotation in enumerate(annotations):
        # Replace the text with a footnote
        message_content.value = message_content.value.replace(annotation.text, f' [{index + 1}]')

        # Gather citations based on annotation attributes
        if (file_citation := getattr(annotation, 'file_citation', None)):
            # Retrieve the cited file details (dummy response here since we can't call OpenAI)
            cited_file = {'filename': 'cited_document.pdf'}  # This should be replaced with actual file retrieval
            citations.append(f'[{index + 1}] {file_citation.quote} from {cited_file["filename"]}')
        elif (file_path := getattr(annotation, 'file_path', None)):
            # Placeholder for file download citation
            cited_file = {'filename': 'downloaded_document.pdf'}  # This should be replaced with actual file retrieval
            citations.append(f'[{index + 1}] Click [here](#) to download {cited_file["filename"]}')  # The download link should be replaced with the actual download path

    # Add footnotes to the end of the message content
    full_response = message_content.value + '\n\n' + '\n'.join(citations)
    return full_response

# Sidebar option for users to upload their own files
uploaded_file = st.sidebar.file_uploader("Upload a file to OpenAI embeddings", key="file_uploader")


def upload_to_openai(filepath):
    """Upload a file to OpenAI and return its file ID."""
    with open(filepath, "rb") as file:
        response = openai.files.create(file=file.read(), purpose="assistants")
    return response.id

# Button to upload a user's file and store the file ID
if st.sidebar.button("Upload File"):
    # Upload file provided by user
    if uploaded_file:
        with open(f"{uploaded_file.name}", "wb") as f:
            f.write(uploaded_file.getbuffer())
        additional_file_id = upload_to_openai(f"{uploaded_file.name}")
        st.session_state.file_id_list.append(additional_file_id)
        st.sidebar.write(f"Additional File ID: {additional_file_id}")
        # Associate the new file with the assistant
        associate_files_with_assistant([additional_file_id], assistant_id)

# Display all file IDs
if st.session_state.file_id_list:
    st.sidebar.write("Uploaded File IDs:")
    for file_id in st.session_state.file_id_list:
        st.sidebar.write(file_id)
        # Associate files with the assistant
        assistant_file = openai.beta.assistants.files.create(
            assistant_id=assistant_id, 
            file_id=file_id
        )
        print(assistant_file)

# Main chat interface setup
st.title("OpenAI Assistants API Chat")
st.write("This is a simple chat application that uses OpenAI's API to generate responses.")


if "openai_model" not in st.session_state:
    st.session_state.openai_model = "gpt-4-1106-preview"
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display existing messages in the chat
#for message in st.session_state.messages:
 #   with st.chat_message(message["role"]):
  #      st.markdown(message["content"])


# Chat input for the user
company_description = st.text_input("What does your company do")
innovation_details = st.text_area("State the innovation")

# Add a submit button
submit_button = st.button("Submit")

# Check if either of the inputs is provided
if submit_button and (company_description or innovation_details):
    # Add user messages to the state and display them
    if company_description:
        st.session_state.messages.append({"role": "user", "content": company_description})
    if innovation_details:
        st.session_state.messages.append({"role": "user", "content": innovation_details})
   # Associate all files with the assistant before making the query
    associate_files_with_assistant(st.session_state.file_id_list, assistant_id)
    # Create thread
    if not st.session_state.thread_id:
        thread = openai.beta.threads.create()
        st.session_state.thread_id = thread.id

    # Format the query for OpenAI
    query = f"We are running a company that {company_description}. Our innovation is {innovation_details}. Please create a suitable R&D project for the company."

    # Add the user's message to the existing thread
    openai.beta.threads.messages.create(
        thread_id=st.session_state.thread_id,
        role="user",
        content=query
    )
    
    # Create a run with additional instructions
    run = openai.beta.threads.runs.create(
        thread_id=st.session_state.thread_id,
        assistant_id=assistant_id,
        instructions="""Please answer the queries using the knowledge provided in the files.Always answer the following questions. I need information based on the BEIS guidelines, specifically focusing on paragraphs 6-12, 13-14, and 15-18. Here are my queries:

1) Scientific or Technological Advance (para 6): What was the scientific or technological advance sought, as per paragraphs 6-12 of the BEIS guidelines? Note: The advance must be in the overall knowledge or capability in a field of science or technology, not just the company’s own knowledge or capability.

2) Scientific or Technological Uncertainties (para 4, 13, 14): What were the scientific or technological uncertainties involved in the project? The advance must be due to overcoming a scientific or technological uncertainty. Note: Uncertainties that can be resolved through brief discussions or have been overcome in previous projects are not considered technological uncertainties.

3) Overcoming Uncertainties: How and when were these uncertainties actually overcome? Describe the methods, investigations, and analysis used, focusing on successes and failures and their impact on the overall project.

4) Field of Science or Technology (paras 15-18): What was the field of science or technology being advanced? Note: Para 15 defines what is not considered science, excluding work in the arts, humanities, and social sciences.

5) Baseline of Science or Technology: What was the baseline of the science or technology when the project began?

6) Knowledge Deduction by a Competent Professional: Why was the knowledge being sought not readily deducible by a competent professional in the field?
"""
        )

    # Poll for the run to complete and retrieve the assistant's messages
    while run.status != 'completed':
        time.sleep(1)
        run = openai.beta.threads.runs.retrieve(
            thread_id=st.session_state.thread_id,
            run_id=run.id
        )

    # Retrieve messages added by the assistant
    messages = openai.beta.threads.messages.list(
        thread_id=st.session_state.thread_id
    )

    # Process and display assistant messages
    assistant_messages_for_run = [
        message for message in messages 
        if message.run_id == run.id and message.role == "assistant"
    ]
    for message in assistant_messages_for_run:
        full_response = process_message_with_citations(message)
        st.session_state.messages.append({"role": "assistant", "constent": full_response})
        st.write(full_response)

else:
    # Prompt to start the chat
    st.write("Please upload files and click 'Start Chat' to begin the conversation.")
    
    
    
    