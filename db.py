import pymysql
import pymysql.cursors

def get_connection():
    try:
        connection = pymysql.connect(
            host='127.0.0.1',
            database='librariedb',
            user='root',
            password='10ianuarie',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        return connection
    except pymysql.MySQLError as e:
        print(f"Eroare la conectarea la baza de date: {e}")
        return None