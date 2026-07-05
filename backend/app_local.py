import os
import re
import sqlite3
import numpy as np
import pandas as pd
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool
import requests
from io import BytesIO
from PIL import Image
from rembg import remove
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# [설정]
master_data = {}
PROCESSED_DIR = os.path.join(os.getcwd(), "static", "processed_imgs")
os.makedirs(PROCESSED_DIR, exist_ok=True)
engine = None  # 로컬 DB 엔진

# ---------------------------------------------------------
# [헬퍼] MySQL 덤프 -> SQLite 변환기 (라인 단위 철벽 필터링)
# ---------------------------------------------------------
def clean_mysql_dump(sql_script):
    """
    파일을 줄 단위로 읽으면서 'persona_item' 관련 내용만 쏙 골라냅니다.
    바이너리 데이터가 섞인 다른 테이블은 아예 무시합니다.
    """
    print("🧹 SQL 스크립트 정제 중... (persona_item 테이블만 추출)")
    
    # 1. 텍스트를 줄 단위로 분리 (바이너리 섞인 ; 분리 방식 폐기)
    lines = sql_script.split('\n')
    
    filtered_lines = []
    is_inside_target_table = False # 타겟 테이블(persona_item) 생성 구문 안에 있는지 여부
    
    for line in lines:
        line_stripped = line.strip()
        
        # 빈 줄이나 주석 건너뛰기
        if not line_stripped or line_stripped.startswith('--') or line_stripped.startswith('/*'):
            continue

        # [CREATE TABLE 감지]
        if line_stripped.upper().startswith('CREATE TABLE'):
            if 'persona_item' in line_stripped:
                is_inside_target_table = True
                filtered_lines.append(line) # 저장 시작
            else:
                is_inside_target_table = False # 다른 테이블이면 무시 모드
            continue
        
        # [CREATE 문 내부 내용 저장]
        if is_inside_target_table:
            filtered_lines.append(line)
            # 테이블 정의 끝(';')을 만나면 모드 해제 (단, 다음 줄이 또 있을 수 있으므로 플래그만 관리)
            if line_stripped.endswith(';'):
                is_inside_target_table = False
            continue

        # [INSERT 문 감지]
        if line_stripped.upper().startswith('INSERT INTO'):
            if 'persona_item' in line_stripped:
                filtered_lines.append(line) # persona_item 데이터만 저장
            # 다른 테이블의 INSERT(특히 brand)는 그냥 버림 (여기가 핵심!)
            continue
            
    # 추출된 줄들만 합치기
    clean_script = '\n'.join(filtered_lines)

    # 2. SQLite 호환 문법으로 치환 (기존 로직 적용)
    clean_script = re.sub(r'ENGINE=.*?;', ';', clean_script)
    clean_script = re.sub(r'DEFAULT CHARSET=.*?;', ';', clean_script)
    clean_script = re.sub(r'COLLATE=.*?;', ';', clean_script)
    clean_script = re.sub(r'ROW_FORMAT=.*?;', ';', clean_script)
    
    # 컬럼 옵션 제거
    clean_script = re.sub(r'COLLATE\s+[\w_]+', '', clean_script)
    clean_script = re.sub(r'CHARACTER SET\s+[\w_]+', '', clean_script)
    
    # MySQL 전용 키워드 제거 (KEY, CONSTRAINT 등)
    # 괄호 사이의 KEY 문법 등을 제거하기 위해 정교한 정규식 사용은 위험하므로
    # 단순 문자열 치환과 라인 단위 정제로 해결
    clean_script = re.sub(r',\s*KEY\s+.*', ',', clean_script) # 한 줄에 있는 KEY 정의 제거
    clean_script = re.sub(r',\s*UNIQUE KEY\s+.*', ',', clean_script)
    clean_script = re.sub(r',\s*CONSTRAINT\s+.*', ',', clean_script)
    
    # 마지막 정리
    clean_script = clean_script.replace('AUTO_INCREMENT', '')
    clean_script = clean_script.replace('unsigned', '')
    clean_script = clean_script.replace('`', '') 
    
    # 혹시 모를 콤마 정리 (끝부분에 ,가 남으면 에러나므로)
    # CREATE TABLE ( ... , ); 같은 문법 오류 방지
    clean_script = re.sub(r',\s*\)', ')', clean_script) 

    return clean_script

# ---------------------------------------------------------
# [초기화] 데이터 로드 및 로컬 DB 구축
# ---------------------------------------------------------
def init_local_system():
    global master_data, engine
    
    # 1. master_data.npz 로드
    try:
        path = 'master_data.npz'
        if not os.path.exists(path):
            print(f"🚨 [오류] {path} 파일이 없습니다. preprocess_local.py를 먼저 실행하세요.")
            return
        
        data = np.load(path, allow_pickle=True)
        required_keys = ['ids', 'names', 'prices', 'imgs', 'cats', 'name_vecs', 'brand_vecs', 'img_vecs', 'cat_vecs']
        temp_data = {}
        for key in required_keys:
            val = data[key]
            if key.endswith('_vecs'):
                try:
                    if val.dtype == object or isinstance(val, list):
                        temp_data[key] = np.array([np.array(x, dtype=np.float32) for x in val])
                    else:
                        temp_data[key] = val.astype(np.float32)
                except:
                    temp_data[key] = val
            else:
                temp_data[key] = val
        master_data = temp_data
        print(f"✅ Master Data 로드 완료! (총 {len(master_data['ids'])}개)")
    except Exception as e:
        print(f"❌ 데이터 로딩 에러: {e}")

    # 2. SQL 파일로 인메모리 DB 생성
    sql_file = 'musinsa_db_dump.sql'
    if not os.path.exists(sql_file):
        print(f"🚨 [치명적 오류] {sql_file} 파일이 없습니다! 로컬 모드를 실행할 수 없습니다.")
        return

    print(f"📂 {sql_file} 로드 및 DB 구축 중...")
    
    raw_sql = ""
    try:
        # [1차] UTF-8
        with open(sql_file, 'r', encoding='utf-8') as f:
            raw_sql = f.read()
    except UnicodeDecodeError:
        try:
            # [2차] CP949
            print("⚠️ UTF-8 로드 실패. CP949 모드로 재시도합니다...")
            with open(sql_file, 'r', encoding='cp949') as f:
                raw_sql = f.read()
        except Exception:
            # [3차] 강제 로드
            print("⚠️ 모든 인코딩 실패. 강제 로드 모드(errors='replace')로 실행합니다.")
            with open(sql_file, 'r', encoding='utf-8', errors='replace') as f:
                raw_sql = f.read()

    try:
        # 읽어온 SQL 정제 및 실행
        clean_sql = clean_mysql_dump(raw_sql)
        
        if not clean_sql.strip():
            print("🚨 [경고] 정제된 SQL이 비어있습니다. 'persona_item' 테이블이 덤프 파일에 있는지 확인하세요.")

        # SQLite 인메모리 엔진 생성
        engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
        
        with engine.connect() as conn:
            conn.connection.cursor().executescript(clean_sql)
            conn.commit()
            
            # 검증: 데이터가 잘 들어갔는지 확인
            result = conn.execute(text("SELECT count(*) FROM persona_item")).scalar()
            print(f"✅ 로컬 DB(SQLite) 구축 완료! (persona_item 데이터: {result}개)")
            
    except Exception as e:
        print(f"❌ 로컬 DB 구축 실패: {e}")
        # 디버깅용: 실패 시 변환된 SQL의 앞부분 출력
        # print("--- Failed SQL Start ---")
        # print(clean_sql[:1000])

init_local_system()

# ---------------------------------------------------------
# [API] 가격 범위 API
# ---------------------------------------------------------
@app.route('/api/price-ranges', methods=['GET'])
def get_price_ranges():
    if not master_data: return jsonify({"error": "Data not loaded"}), 500
    
    CATEGORY_MAP = {"outer": "아우터", "top": "상의", "bottom": "바지", "shoes": "신발", "acc": "액세서리"}
    category_price_ranges = {}
    for eng_key, kor_val in CATEGORY_MAP.items():
        cat_mask = (master_data['cats'] == kor_val)
        prices = master_data['prices'][cat_mask]
        if len(prices) > 0:
            category_price_ranges[eng_key] = {"min": int(np.min(prices)), "max": int(np.max(prices))}
        else:
            category_price_ranges[eng_key] = {"min": 0, "max": 0}
    return jsonify(category_price_ranges)

# ---------------------------------------------------------
# [기능] 이미지 처리
# ---------------------------------------------------------
def process_and_save_image(image_url, save_path):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(image_url, headers=headers, timeout=10)
        if response.status_code == 200:
            input_image = Image.open(BytesIO(response.content)).convert("RGBA")
            output_image = remove(input_image)
            output_image.save(save_path, format="PNG")
            return True
        return False
    except:
        return False

# ---------------------------------------------------------
# [API] 상품 추천 (로컬 DB 사용)
# ---------------------------------------------------------
@app.route('/api/products', methods=['GET'])
def get_recommendations():
    persona = request.args.get('persona', '아메카지')
    fixed_outfit_id = request.args.get('outfit_id')
    target_category_filter = request.args.get('category') 
    
    if not master_data or not engine: return jsonify({"error": "System not ready"}), 500

    try:
        with engine.connect() as conn:
            if fixed_outfit_id:
                selected_outfit = int(fixed_outfit_id)
            else:
                # 테이블 존재 여부 확인 (안전장치)
                check_table = text("SELECT name FROM sqlite_master WHERE type='table' AND name='persona_item'")
                if not conn.execute(check_table).fetchone():
                    return jsonify({"error": "DB Table 'persona_item' not found"}), 500

                outfit_query = text("SELECT DISTINCT outfit FROM persona_item WHERE persona = :persona")
                outfits_df = pd.read_sql(outfit_query, conn, params={"persona": persona})
                
                if outfits_df.empty: 
                    print(f"⚠️ Warning: '{persona}' 페르소나 데이터 없음. 기본값 1 사용.")
                    selected_outfit = 1 
                else:
                    selected_outfit = int(np.random.choice(outfits_df['outfit'].tolist()))

            item_query = text("SELECT product_id FROM persona_item WHERE persona = :persona AND outfit = :outfit")
            target_ids = pd.read_sql(item_query, conn, params={"persona": persona, "outfit": selected_outfit})['product_id'].tolist()
            
            if not target_ids: 
                print("⚠️ Warning: Outfit 매칭 실패. 랜덤 추천으로 대체합니다.")
                target_ids = list(master_data['ids'][:5])

        # 이후 로직은 기존과 동일
        target_indices = np.where(np.isin(master_data['ids'], target_ids))[0]
        if len(target_indices) == 0:
             target_indices = [0, 1, 2, 3, 4]

        target_item_map = {master_data['cats'][idx]: idx for idx in target_indices}
        CATEGORY_MAP = {"outer": "아우터", "top": "상의", "bottom": "바지", "shoes": "신발", "acc": "액세서리"}
        final_response = { "current_outfit_id": selected_outfit, "items": {} }

        for eng_key, kor_val in CATEGORY_MAP.items():
            if target_category_filter and target_category_filter != eng_key: continue
            
            if kor_val not in target_item_map:
                final_response["items"][eng_key] = []
                continue

            target_idx = target_item_map[kor_val]
            cat_min = request.args.get(f'min_{eng_key}', type=int)
            cat_max = request.args.get(f'max_{eng_key}', type=int)

            # 유사도 계산
            sim_name = np.dot(master_data['name_vecs'], master_data['name_vecs'][target_idx])
            sim_brand = np.dot(master_data['brand_vecs'], master_data['brand_vecs'][target_idx])
            sim_img = np.dot(master_data['img_vecs'], master_data['img_vecs'][target_idx])
            sim_cat = np.dot(master_data['cat_vecs'], master_data['cat_vecs'][target_idx])
            final_scores = (sim_name * 0.1) + (sim_brand * 0.1) + (sim_img * 0.6) + (sim_cat * 0.1)

            price_mask = np.ones(len(master_data['prices']), dtype=bool)
            if cat_min: price_mask &= (master_data['prices'] >= cat_min)
            if cat_max: price_mask &= (master_data['prices'] <= cat_max)

            combined_mask = (master_data['cats'] == kor_val) & price_mask
            cat_scores = final_scores[combined_mask]
            cat_real_indices = np.where(combined_mask)[0]
            
            if len(cat_scores) == 0:
                final_response["items"][eng_key] = []
                continue

            sorted_indices = np.argsort(cat_scores)[::-1][:100]
            selected_local = np.random.choice(sorted_indices, min(5, len(sorted_indices)), replace=False)
            
            items_list = []
            for loc_idx in selected_local:
                original_idx = cat_real_indices[loc_idx]
                p_id = int(master_data['ids'][original_idx])
                
                # 이미지 경로 처리
                processed_filename = f"nobg_{p_id}.png"
                processed_file_path = os.path.join(PROCESSED_DIR, processed_filename)
                
                if os.path.exists(processed_file_path):
                    final_img_url = f"{request.host_url}static/processed_imgs/{processed_filename}"
                else:
                    success = process_and_save_image(master_data['imgs'][original_idx], processed_file_path)
                    final_img_url = f"{request.host_url}static/processed_imgs/{processed_filename}" if success else master_data['imgs'][original_idx]

                items_list.append({
                    "product_id": p_id,
                    "product_name": str(master_data['names'][original_idx]),
                    "price": int(master_data['prices'][original_idx]),
                    "img_url": final_img_url,
                    "category": kor_val,
                })
            final_response["items"][eng_key] = items_list

        return jsonify(final_response)

    except Exception as e:
        print(f"❌ 추천 로직 에러: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/static/processed_imgs/<path:filename>')
def serve_processed_image(filename):
    return send_from_directory(PROCESSED_DIR, filename)

if __name__ == '__main__':
    print("🚀 로컬 모드 서버 시작 (포트 5000)")
    app.run(debug=True, port=5000)