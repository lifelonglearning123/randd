# Import necessary libraries
import openai
from openai import OpenAI
import streamlit as st
import time
from decouple import config  # Import config from decouple
import test
import technology_summary

# Set your OpenAI Assistant ID here
assistant_id = 'asst_ct2tGsfN0xrDG3RzTCaeoa6M'

openai = OpenAI(default_headers={"OpenAI-Beta": "assistants=v1"})

# Initialize the OpenAI client (ensure to set your API key in the sidebar within the app)
openai.api_key = config("OPENAI_API_KEY")  # Use config to get the API key

# Initialize session state variables for file IDs and chat control

if "thread_id" not in st.session_state:
    st.session_state.thread_id = None

if "file_id_list" not in st.session_state:
    st.session_state.file_id_list = []
# Set up the Streamlit page with a title and icon
st.set_page_config(page_title="ChatGPT-like Chat App", page_icon=":speech_balloon:")

full_response = ""
# The full_response_completed variable is to control if the second submit button is shown or not.
if "full_response_completed" not in st.session_state:
    st.session_state.full_response_completed = False


# The full_response_completed variable is to control if the second submit button is shown or not.
if "full_response" not in st.session_state:
    st.session_state.full_response = ""
    
    
    
# Function to associate files with the assistant
def associate_files_with_assistant(file_ids, assistant_id):
    for file_id in file_ids:
        openai.beta.assistants.files.create(
            assistant_id=assistant_id, 
            file_id=file_id
            
        )
        print(type(file_ids))
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


# Main chat interface setup
st.title("macaws R&D Assistant")
st.write("Speedup R&D application.")


if "openai_model" not in st.session_state:
    st.session_state.openai_model = "gpt-4-turbo"
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
submit_button = st.button("AI Summary-Start")

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
        instructions="""        Qu1: Scientific or Technological Advance : What was the scientific or technological advance sought? Note: The advance must be in the overall knowledge or capability in a field of science or technology, not just the company’s own knowledge or capability.6. An advance in science or technology means an advance in overall knowledge or capability in a field of science or technology (not a company’s own state of knowledge or capability alone). This includes the adaptation of knowledge or capability from another field of science or technology in order to make such an advance where this adaptation was not readily deducible. An advance in science or technology may have tangible consequences (such as a new or more efficient cleaning product, or a process which generates less waste) or more intangible outcomes (new knowledge or cost improvements, for example).8. A process, material, device, product, service or source of knowledge does not become an advance in science or technology simply because science or technology is used in its creation. Work which uses science or technology but which does not advance scientific or technological capability as a whole is not an advance in science or technology. A project which seeks to, for example,a) extend overall knowledge or capability in a field of science or technology; or b) create a process, material, device, product or service which incorporates or represents an increase in overall knowledge or capability in a field of science or technology; or c) make an appreciable improvement to an existing process, material, device, product or service through scientific or technological changes; or d) use science or technology to duplicate the effect of an existing process, material, device, product or service in a new or appreciably improved way (e.g. a product which has exactly the same performance characteristics as existing models, but is built in a fundamentally different manner) will therefore be R&D. Even if the advance in science or technology sought by a project is not achieved or not fully realised, R&D still takes place. If a particular advance in science or technology has already been made or attempted but details are not readily available (for example, if it is a trade secret), work to achieve such an advance can still be an advance in science or technology. However, the routine analysis, copying or adaptation of an existing product, process, service or material, will not be an advance in science or technology.
        Qu2: Scientific or Technological Uncertainties: What were the scientific or technological uncertainties involved in the project? The advance must be due to overcoming a scientific or technological uncertainty. Note: Uncertainties that can be resolved through brief discussions or have been overcome in previous projects are not considered technological uncertainties. The activities which directly contribute to achieving this advance in science or technology through the resolution of scientific or technological uncertainty are R&D.13. Scientific or technological uncertainty exists when knowledge of whether something is scientifically possible or technologically feasible, or how to achieve it in practice, is not readily available or deducible by a competent professional working in the field. This includes system uncertainty. Scientific or technological uncertainty will often arise from turning something that has already been established as scientifically feasible into a cost-effective, reliable and reproducible process, material, device, product or service. 14. Uncertainties that can readily be resolved by a competent professional working in the field are not scientific or technological uncertainties. Similarly, improvements, optimisations and fine-tuning which do not materially affect the underlying science or technology do not constitute work to resolve scientific or technological uncertainty.
        Qu3 : Overcoming Uncertainties: How and when were these uncertainties actually overcome? Describe the methods, investigations, and analysis used, focusing on successes and failures and their impact on the overall project.
        Qu4 : Field of Science or Technology (paras 15-18): What was the field of science or technology being advanced? Note: Para 15 defines what is not considered science, excluding work in the arts, humanities, and social sciences.15A. Science is the systematic study of the nature and behaviour of the physical and material universe. Work in the arts, humanities and social sciences, including economics, is not science for the purpose of these Guidelines. Mathematical techniques are frequently used in science. From April 2023 mathematical advances in themselves are treated as science for the purposes of these Guidelines, whether or not they are advances in representing the nature and behaviour of the physical and material universe. These Guidelines apply equally to work in any branch or field of science. Technology is the practical application of scientific principles and knowledge, where ‘scientific’ is based on the definition of science above. These Guidelines apply equally to work in any branch or field of technology.
        Qu5 : Baseline of Science or Technology: What was the baseline of the science or technology when the project began?
        Qu6 : Knowledge Deduction by a Competent Professional: Why was the knowledge being sought not readily deducible by a competent professional in the field?
        Qu7 : Please provide a list of the competent professionals involved in the project, including their qualifications, experience and what work they did for the project
"""
        )
    print("The assistant id is: ", assistant_id)
    print("The thread id is: ", st.session_state.thread_id)
    # Poll for the run to complete and retrieve the assistant's messages
    while run.status != 'completed':
        time.sleep(1)
        run = openai.beta.threads.runs.retrieve(
            thread_id=st.session_state.thread_id,
            run_id=run.id
        )
        print("The run status is: ", run.status)
        print("The run id is: ", run.id)
    print("checking     1")     
    # Retrieve messages added by the assistant
    messages = openai.beta.threads.messages.list(
        thread_id=st.session_state.thread_id
    )

    # Process and display assistant messages
    assistant_messages_for_run = [
        message for message in messages 
        if message.run_id == run.id and message.role == "assistant"
    ]
    print("program reached print")
    for message in assistant_messages_for_run:
        full_response = process_message_with_citations(message)
        st.session_state.messages.append({"role": "assistant", "constent": full_response})
        # Indicate that the initial process has been completed
        st.session_state.full_response = full_response
        st.session_state.full_response_completed = True
        print('message is:', message)
    #print(full_response)
    st.write(st.session_state.full_response)
    print("Program reached end")
    
    
if st.session_state.full_response_completed:
    if st.button("Full Response-Start"):
        st.write(st.session_state.full_response)
        # Reset the process completion state if needed or start the next part of your application
        st.session_state.full_response_completed = False
        # You can add your logic here for what happens when the "Start" button is pressed

        summary_response = technology_summary.summary(st.session_state.full_response)
        st.write("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        st.write(summary_response)  
        final_response=test.hmrc_randd_qu(summary_response)
        for key, value in final_response.items():
            st.write(value)
            st.write("*************")
            print(value)
            print("******************")

        # At the end of your Streamlit app, where you want to delete the uploaded files
        if st.session_state.file_id_list:  # Check if there are any file IDs to delete
            for file_id in st.session_state.file_id_list:
                try:
                    openai.File.delete(file_id=file_id)  # Use openai.File.delete to delete the file
                    st.write(f"Deleted file ID: {file_id}")  # Optional: Confirm deletion in the app
                except Exception as e:
                    st.error(f"Error deleting file ID {file_id}: {e}")  # Handle exceptions


else:
    # Prompt to start the chat
    st.write("Please upload files and click 'Start Chat' to begin the conversation.")
    
    
    
    
