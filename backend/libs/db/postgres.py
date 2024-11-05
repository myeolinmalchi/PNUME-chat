from VectorDB import VectorDB as DB
from config import configurataion as config
from openai import OpenAI
import tiktoken

myDB = DB(config["host"], config["port"], config["database"], config["user"], config["password"])
client = OpenAI(api_key = config["openai_api_key"])

extention_install_query = "CREATE EXTENSION vector;"
enum_query = """CREATE TYPE set AS ENUM ('공지/학부', '공지/대학원', '공지/장학', '공지/홍보', '학부 소식', '언론 속 학부', '세미나', '취업정보');"""



def create_table_query(table_name:str) -> str:
    """This function creates a table. The configuration of column is fixed."""
    query = f"""
        CREATE TABLE public.{table_name}
        (pk_id SERIAL PRIMARY KEY,
        notice_id INT NOT NULL,
        title  VARCHAR NOT NULL,
        date   DATE    NOT NULL,
        writer VARCHAR  NOT  NULL,
        content VARCHAR NOT NULL,
        category set  NOT  NULL,
        attached VARCHAR   NULL,
        embedding vector(256)
        );
    """
    return query

def delete_table_query(table_name:str) -> str:
    """This function deletes specified table."""
    query = f"DROP TABLE {table_name}"
    return query

def insert_query(table_name:str, notice_id:int, title:str, date:str, writer:str, content:str, category:str, attached:str) -> str:
    """"This function inserts a row in specified table.
        If there's no value for a parameter, set the parameter as string NULL."""
    query = f"""INSERT INTO 	{table_name} (pk_id, notice_id, title, date, writer, content, category, attached, embedding)
                VALUES 	(DEFAULT, '{notice_id}', '{title}', '{date}', '{writer}', '{content}', '{category}', """
    #from this line, attached is added to query.
    if attached == "NULL":
        query += "NULL, "
    else:
        query += f"'{attached}', "
    #from this line, content is embedded into 256 dimensional vector and added to query. OpenAi embedding is used.
    embedding = get_embedding(content)
    query += f"vector('{embedding}')"
    #close the sql instruction
    query += ");"
    return query

def vector_similarity_query(question_vector:list[float], limit:int) -> str:
    """This function retrieve rows with closest vector embedding within the number of limit."""
    query = f"SELECT pk_id, notice_id, title, date, writer, content, category, attached FROM notice ORDER BY embedding <=> vector('{question_vector}') LIMIT {limit};"
    return query

def measure_similarity_query(question_vector:list[float], limit:int) -> str:
    """This function retrieve cosin similarity scores with closest vector embedding within the number of limit."""
    query = f"SELECT title, 1 - (embedding <=> '{question_vector}') AS cosine_similarity FROM notice ORDER BY (embedding <=> '{question_vector}') LIMIT {limit};"
    return query

def get_similar_info_query(question:str) -> str:
    """This function turns the question in string format into embedding vector of 256 dimensions and find the most similar row of a table."""
    question_embedding = get_embedding(question)
    info = vector_similarity_query(question_embedding, 1)
    return info

def get_embedding(text:str, model=config["embedding_model"], dimensions:int = 256) -> list[float]:
   """This function retrieve embedding vector of the text input."""
   return client.embeddings.create(input = [text], model=model, dimensions = dimensions).data[0].embedding

def get_num_embedding_token(string:str, model=config["embedding_model"]) -> int:
    """This function calculate the number of tokens. You can use this function before invocating an API."""
    encoding = tiktoken.encoding_for_model(model)
    num_of_tokens = len(encoding.encode(string))
    return num_of_tokens