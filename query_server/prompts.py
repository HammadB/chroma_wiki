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
    input_variables=["history", "context", "question"],
    template="""You are an intelligent AI assistant trained by Chroma in a chat converation between you and a human. Answer the humans questions as specifically as possible and with as much detail as possible using the provided context before the question. If the answer is not contained within the text below, say "I don't know". Do not speak off topic to the question, make sure to answer the question in full. 
=== CHAT HISTORY ===
{history}

=== CONTEXT FOR QUESTION ===
{context}

Human: {question}
AI:""")

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
