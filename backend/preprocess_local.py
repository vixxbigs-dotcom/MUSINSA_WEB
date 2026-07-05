import pandas as pd
import sqlite3
import os
import re
import numpy as np

# [설정]
SQL_FILE = 'musinsa_db_dump.sql'
OUTPUT_FILE = 'master_data.npz'

def clean_mysql_dump(sql_script):
    """MySQL 덤프 정제 (app_local.py와 동일 로직)"""
    script = sql_script
    script = re.sub(r'/\*.*?\*/;', '', script, flags=re.DOTALL)
    script = re.sub(r'^SET .*?;', '', script, flags=re.MULTILINE)
    script = re.sub(r'^LOCK TABLES .*?;', '', script, flags=re.MULTILINE)
    script = re.sub(r'^UNLOCK TABLES;', '', script, flags=re.MULTILINE)
    script = re.sub(r'ENGINE=.*?;', ';', script)
    script = re.sub(r'DEFAULT CHARSET=.*?;', ';', script)
    script = re.sub(r'COLLATE=.*?;', ';', script)
    script = script.replace('AUTO_INCREMENT', '')
    script = script.replace('unsigned', '')
    script = script.replace('`', '')
    return script

def create_master_data_local():
    print("🔄 [로컬 모드] 마스터 데이터 생성 시작...")
    
    if not os.path.exists(SQL_FILE):
        print(f"🚨 {SQL_FILE} 파일이 없습니다.")
        return

    try:
        # 1. SQLite 임시 DB 생성
        conn = sqlite3.connect(':memory:')
        cursor = conn.cursor()
        
        print("📂 SQL 파일 읽는 중...")
        with open(SQL_FILE, 'r', encoding='utf-8') as f:
            clean_sql = clean_mysql_dump(f.read())
            cursor.executescript(clean_sql)
        conn.commit()
        
        # 2. 데이터 추출
        print("extracting data from SQLite...")
        query = """
            SELECT p.product_id, p.product_name, p.original_price, p.img_url, 
                   c.upper_category, c.lower_category
            FROM product p 
            JOIN category c ON p.category_id = c.category_id
        """
        df = pd.read_sql(query, conn)
        conn.close()
        
        print(f"✅ {len(df)}개 상품 로드 완료")
        
        # 3. (여기부터는 기존 벡터화 로직을 넣어야 합니다)
        # 만약 벡터 데이터가 이미 다른 파일에 있거나 새로 만들어야 한다면 
        # 기존 preprocess.py의 벡터 생성 로직을 여기에 복사해와야 합니다.
        # 단순히 테스트용이라면 빈 벡터로 채울 수도 있습니다.
        
        # [예시: 기존 데이터가 있는 경우 업데이트만 하는 방식]
        # 여기서는 단순히 SQL에서 읽은 정보만 출력하고 종료합니다.
        # 실제로는 기존 코드의 벡터 생성 부분(FAISS 등)을 여기에 붙여넣으세요.
        
    except Exception as e:
        print(f"❌ 데이터 생성 실패: {e}")

if __name__ == "__main__":
    create_master_data_local()