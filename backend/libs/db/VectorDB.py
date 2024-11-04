import textwrap
from typing import List
import psycopg2

class VectorDB:
    _connection = None

    def __init__(self, host:str, port:str, database:str, user:str, password:str):
        self.__host = host
        self.__port = port
        self.__database = database
        self.__user = user
        self.__password = password


    def connect(self) -> None:
        """This function sets connection for DB, the timezone, and the search path as public."""
        connection = psycopg2.connect(
            host=self.__host,
            port=self.__port,
            database=self.__database,
            user=self.__user,
            password=self.__password,
        )

        cursor = connection.cursor()
        cursor.execute("SET TIMEZONE TO 'Asia/Seoul'")
        cursor.execute(f"SET search_path TO 'public'")
        cursor.close()

        self.__connection = connection

    def close(self) -> None:
        """This function closes the connection to DB."""
        if self.__connection is not None:
            self.__connection.close()
            self.__connection = None


    def execute_query(self, query: str) -> None:
        """Put the single query into list and pass it to execute_queries."""
        self.execute_queries([query])

    def execute_queries(self, queries: List[str]) -> None:
        """Excute queries for CREATE, UPDATE, DELETE."""
        queries = [textwrap.dedent(query) for query in queries]

        connection = self.get_connection()
        for query in queries:
            if query.strip(): #if query is empty, skip the following process.
                cursor = connection.cursor()
                cursor.execute(query)
                connection.commit()
                cursor.close()
                
    def fetch_query(self, query: str):
        """Excute query for READ"""
        query = textwrap.dedent(query)

        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()

        return result

    def explain_analyze_query(self, query: str):
        """This method returns the analysis of query"""
        query = textwrap.dedent(f"EXPLAIN ANALYZE {query}")

        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute(query)
        result = cursor.fetchall() 
        cursor.close()

        return result

    def get_connection(self):
        """If the DB is closed, open it up."""
        self.connect()
        return self.__connection
