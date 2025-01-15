from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_community.utilities import SQLDatabase
from langchain_core.output_parsers import StrOutputParser
import streamlit as st
import os
from langchain_huggingface import HuggingFaceEndpoint
from langchain_huggingface import HuggingFaceEmbeddings


load_dotenv()

# Step 1: Setup LLM (Mistral with HuggingFace)
HF_TOKEN=os.environ.get("HF_TOKEN")
HUGGINGFACE_REPO_ID="mistralai/Mistral-7B-Instruct-v0.3"




def init_database(user: str, password: str, host: str, port: str, database: str) -> SQLDatabase:
  db_uri = f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}"
  return SQLDatabase.from_uri(db_uri)

def get_sql_chain(db):
  # template = """
  template = """
    You are an intelligent SQL assistant tasked with helping users query a college placement database. 
    The database contains information about students, departments, companies, and placements.
    
    Schema Details:
    {schema}
    
    Conversation History:
    {chat_history}
    
    Your goal is to:
    1. Generate SQL queries based on the user's question.
    2. Ensure queries include only the necessary columns and use proper joins, conditions, and aggregations.
    3. Validate against the schema to avoid referencing non-existent columns or tables.
    
    Example:
    Question: How many students were placed in 2024?
    SQL Query: SELECT COUNT(*) FROM placements WHERE status = 'Placed' AND YEAR(placement_date) = 2024;
    
    Question: Which department has the highest number of placements?
    SQL Query: 
    SELECT d.name AS department_name, COUNT(p.placement_id) AS total_placements
    FROM placements p
    JOIN students s ON p.student_id = s.student_id
    JOIN departments d ON s.department_id = d.department_id
    GROUP BY d.name
    ORDER BY total_placements DESC
    LIMIT 1;
    
    Now, based on the provided schema and conversation history, generate the SQL query:
    Question: {question}
    SQL Query:
    """
    
  prompt = ChatPromptTemplate.from_template(template)
  
  # llm = ChatOpenAI(model="gpt-4-0125-preview")
#   llm = ChatGroq(model="mixtral-8x7b-32768", temperature=0)
#   llm=ChatGroq(groq_api_key=groq_api_key,
#              model_name="Llama3-8b-8192")
  # llm = ChatGroq(api_key=groq_api_key, model="mixtral-8x7b-32768", temperature=0)

  llm=HuggingFaceEndpoint(
        repo_id=HUGGINGFACE_REPO_ID,
        temperature=0.5,
        model_kwargs={"token":HF_TOKEN,
                      "max_length":"512"}
    )
  
  def get_schema(_):
    return db.get_table_info()
  
  return (
    RunnablePassthrough.assign(schema=get_schema)
    | prompt
    | llm
    | StrOutputParser()
  )
    
# def get_response(user_query: str, db: SQLDatabase, chat_history: list):
#   sql_chain = get_sql_chain(db)
  
#   template = """
#     You are a data analyst for a college placement database. Your job is to answer user queries about the placement records.
#     The database contains information about students, departments, companies, and placements.
#     <SCHEMA>{schema}</SCHEMA>

#     Conversation History: {chat_history}
#     SQL Query: <SQL>{query}</SQL>
#     User question: {question}
#     SQL Response: {response}"""
  
#   prompt = ChatPromptTemplate.from_template(template)
  
#   # llm = ChatOpenAI(model="gpt-4-0125-preview")
# #   llm = ChatGroq(model="mixtral-8x7b-32768", temperature=0)
#   # llm = ChatGroq(api_key=groq_api_key, model="mixtral-8x7b-32768", temperature=0)


#   llm=HuggingFaceEndpoint(
#         repo_id=HUGGINGFACE_REPO_ID,
#         temperature=0.5,
#         model_kwargs={"token":HF_TOKEN,
#                       "max_length":"512"}
#     )
  
#   chain = (
#     RunnablePassthrough.assign(query=sql_chain).assign(
#       schema=lambda _: db.get_table_info(),
#       response=lambda vars: db.run(vars["query"]),
#     )
#     | prompt
#     | llm
#     | StrOutputParser()
#   )
  
#   return chain.invoke({
#     "question": user_query,
#     "chat_history": chat_history,
#   })
    

def get_response(user_query: str, db: SQLDatabase, chat_history: list):
    sql_chain = get_sql_chain(db)

    # Execute the SQL chain to get the query result
    sql_query = sql_chain.invoke({
        "question": user_query,
        "chat_history": chat_history,
    })

    # Run the SQL query on the database
    try:
        sql_result = db.run(sql_query)
    except Exception as e:
        return f"An error occurred while executing the query: {str(e)}"

    # Process the result into a clean response
    if sql_result:
        if isinstance(sql_result[0], tuple) and len(sql_result[0]) == 1:
            # If the result is a list of single-value tuples
            result_text = ", ".join(str(row[0]) for row in sql_result)
        else:
            # General case: show the result as is
            result_text = str(sql_result)
    else:
        result_text = "No results found."

    # Construct the response
    response = f"Answer: {result_text}"
    return response






if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
      AIMessage(content="Hello! I'm a SQL assistant. Ask me anything about your database."),
    ]

load_dotenv()

st.set_page_config(page_title="Chat with MySQL", page_icon=":speech_balloon:")

st.title("Chat with MySQL")

with st.sidebar:
    st.subheader("Settings")
    st.write("This is a simple chat application using MySQL. Connect to the database and start chatting.")
    
    st.text_input("Host", value="mysql", key="Host")
    st.text_input("Port", value="3306", key="Port")
    st.text_input("User", value="kavya", key="User")
    st.text_input("Password", type="password", value="kavya", key="Password")
    st.text_input("Database", value="placementdb", key="Database")
    
    if st.button("Connect"):
        with st.spinner("Connecting to database..."):
            db = init_database(
                st.session_state["User"],
                st.session_state["Password"],
                st.session_state["Host"],
                st.session_state["Port"],
                st.session_state["Database"]
            )
            st.session_state.db = db
            st.success("Connected to database!")
    
for message in st.session_state.chat_history:
    if isinstance(message, AIMessage):
        with st.chat_message("AI"):
            st.markdown(message.content)
    elif isinstance(message, HumanMessage):
        with st.chat_message("Human"):
            st.markdown(message.content)

user_query = st.chat_input("Type a message...")
if user_query is not None and user_query.strip() != "":
    st.session_state.chat_history.append(HumanMessage(content=user_query))
    
    with st.chat_message("Human"):
        st.markdown(user_query)
        
    with st.chat_message("AI"):
        response = get_response(user_query, st.session_state.db, st.session_state.chat_history)
        st.markdown(response)
        
    st.session_state.chat_history.append(AIMessage(content=response))