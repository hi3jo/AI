from mysql.connector import Error
import mysql.connector
import pandas as pd

def insert_into_table():
    try:
        
        # MySQL 데이터베이스에 연결
        connection = mysql.connector.connect(
              host='192.168.0.51'    # 로컬호스트
            , database='lawbot_db'   # 사용할 데이터베이스 이름
            , user='root'            # MySQL 사용자 이름
            , password='1234'         # MySQL 사용자 비밀번호
        )

        if connection.is_connected():
            cursor = connection.cursor()
            
            # CSV 파일 읽기
            df = pd.read_csv('../chatDB/crawling2024.csv')
            
            # 각 행을 반복하며 데이터 삽입
            for index, row in df.iterrows():
                
                # 삽입할 데이터 쿼리
                insert_query = """INSERT INTO divorce_precedent (  case_serial_number
                                                                , case_name
                                                                , case_number
                                                                , judgment_date
                                                                , court_name 
                                                                , case_type_name
                                                                , case_type_code  
                                                                , judgment_type
                                                                , sentence
                                                                , issue
                                                                , judgment_summary
                                                                , referenced_statutes
                                                                , referenced_cases
                                                                , case_content) 
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                
                # 삽입할 데이터 값
                record_to_insert = (row['판례일련번호'], row['사건명'], row['사건번호'], row['선고일자'], row['법원명'], row['사건종류명'], row['사건종류코드'], row['판결유형'], row['선고'], row['판시사항'], row['판결요지'], row['참조조문'], row['참조판례'], row['판례내용'])
                cursor.execute(insert_query, record_to_insert)
            
            connection.commit()
            print("Records inserted successfully into table")

    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
    
    finally:
        if connection.is_connected():
            # cursor.close()
            connection.close()
            print("MySQL connection is closed")

if __name__ == "__main__":
    insert_into_table()