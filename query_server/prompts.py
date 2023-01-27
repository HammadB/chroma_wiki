from langchain.prompts import PromptTemplate

answer_with_context = PromptTemplate(
    input_variables=["context", "question"],
    template="""Answer the question as specifically as possible and with as much detail as possible using the provided context. If the answer is not contained within the text below, say "I don't know". Do not speak off topic to the question, make sure to answer the question in full. 
Context: {context}

Q: {question}
A:""")

chat_entry_template = PromptTemplate(
    input_variables=["agent_text", "human_text"],
    template="""Human: {human_text}
AI: {agent_text}"""
)


chat_with_context_template = PromptTemplate(
    input_variables=["context", "question"],
    template=""""You are an AI assistant for Wikipedia. You are given the following extracted parts of a long document and a question. Provide a converstational answer to the question as specifically as possible and with as much detail as possible using the provided context. If the answer is not contained within the extracted text below, say "I don't know". Do not speak off topic to the question, make sure to answer the question in full and do NOT make up an answer.
====
{context}
====
Question: {question}
Answer:""")

chat_summarize_template = PromptTemplate(
    input_variables=["chat_history", "question"],
    template="""Given the following conversation and a follow up question, rephrase the follow up question to be a standalone question by incorporating the conversation history. You should assume that the question is related more to the questions at the end of the history, do not create a new chat history.
 
===
Chat History:
{chat_history}
===
Follow Up Question: {question}
Standalone Question:""")

wikipedia_query_generation = PromptTemplate(
    input_variables=["question"],
    template="""
    
    Please turn the following question into a list of search queries for wikipedia. Each query should help answer the question and be very specific to the question. Put each query on a line. Limit yourself to three queries and do not include more queries than you need. It is better to have fewer queries.
    
    Examples:
    
    Question: Who is Barack Obama and what were his accomplishments?
    Barack Obama 
    
    Question: Can you compare avocadoes to oranges?
    Avocadoes
    Oranges
    
    Question: When was Joseph Pulitzer born and what is the Pulitzer Prize?
    Joseph Pulitzer
    Pulitzer Prize
    
    
    Question: {question}
     """
)
