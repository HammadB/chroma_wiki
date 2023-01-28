# Chroma Wiki

Chroma wiki is a prototype chat-bot based that uses retrieval and query-time searching. It answers users questions but when it does not know the answer it performs a search on Wikipedia for relevant articles, adds them to its knowledge-base and then performs the query again.


https://user-images.githubusercontent.com/5598697/215204840-e697153c-89ce-4f94-9f09-d7138fe8c888.mov


The application consists of a simple react frontend that allows users to ask questions. The backend uses SSE to send query responses to the client as well as transient updates. 

# Getting Started

To get started you will have to run the frontend and backend.

### Frontend

#### 1. From the frontend directory, install the dependencies.

    yarn install

#### 2. Then run 

    yarn start


### Backend

The backend (query_server) is built using python and FastAPI

#### 1. From the query_server directory, install the dependencies.
    
    pip install -r requirements

#### 2. You will need a local BZ2 copy of wikipedia and an index in order to use the query_server. You can download these dumps from wikimedia

    https://dumps.wikimedia.org/enwiki/20230120/

#### 3. Create your .env file from the example

    cp .env.example .env

#### 3. Then update your .env file with the correct values for your local copy of Wikipedia - WIKIPEDIA_LOCAL_INDEX and WIKIPEDIA_LOCAL_DUMP_PATH. You can update the other values later in the process.

    OPENAI_API_KEY="<YOUR_API_KEY>"
    WIKI_DB_PATH="wikipedia_db_saves/<YOUR_PATH_HERE>"
    INDEX_PATH="index_saves/<YOUR_PATH_HERE>"
    WIKIPEDIA_LOCAL_INDEX_PATH="/path/to/your/enwiki-20230101-pages-articles-multistream-index.txt"
    WIKIPEDIA_LOCAL_DUMP_PATH="/path/to/your/enwiki-20230101-pages-articles-multistream.xml.bz2"

#### 4. Then scrape Wikipedia and build the indices required. This will save the scraped data and NN index. Update your WIKI_DB_PATH and INDEX_PATH in your .env file with those values after. This step may take a while.
    
    python build_indices.py

#### 5. Run the server
    
    uvicorn main:app --reload



