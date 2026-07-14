import base64
import html
import random
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st


# ============================================================
# MUSINSA PERSONA LITE
# React 원본 App.js / App.css 구조를 Streamlit으로 최대한 이식한 버전
# ============================================================

st.set_page_config(
    page_title="MUSINSA X PERSONA",
    page_icon="🖤",
    layout="wide",
    initial_sidebar_state="collapsed",
)

BASE_DIR = Path(__file__).resolve().parent

# 원본 프로젝트 경로
FONT_DIR = BASE_DIR / "frontend" / "src" / "assets" / "fonts"
BACKGROUND_DIR = BASE_DIR / "frontend" / "public" / "backgrounds"
WOMEN_SNAP_DIR = BASE_DIR / "frontend" / "public" / "persona" / "women" / "snaps"
WOMEN_SUBGROUP_DIR = WOMEN_SNAP_DIR / "subgroup"

# Streamlit Lite 추천 데이터
MASTER_DATA_PATH = BASE_DIR / "data" / "lite" / "master_data_lite.npz"
PERSONA_ITEM_PATH = BASE_DIR / "data" / "lite" / "persona_item_lite.csv"


# ============================================================
# 1. 원본 스타일 이식
# ============================================================

def file_to_base64(path: Path) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def local_image_src(path: Path) -> str | None:
    if not path or not path.exists():
        return None

    suffix = path.suffix.lower().replace(".", "")
    if suffix == "jpg":
        suffix = "jpeg"

    return f"data:image/{suffix};base64,{file_to_base64(path)}"


def build_font_css() -> str:
    light = FONT_DIR / "musinsa-Light.ttf"
    medium = FONT_DIR / "musinsa-Medium.ttf"
    bold = FONT_DIR / "musinsa-Bold.ttf"

    if not (light.exists() and medium.exists() and bold.exists()):
        return ""

    return f"""
    @font-face {{
      font-family: 'MusinsaFont';
      src: url(data:font/ttf;base64,{file_to_base64(light)}) format('truetype');
      font-weight: 200;
    }}
    @font-face {{
      font-family: 'MusinsaFont';
      src: url(data:font/ttf;base64,{file_to_base64(medium)}) format('truetype');
      font-weight: 500;
    }}
    @font-face {{
      font-family: 'MusinsaFont';
      src: url(data:font/ttf;base64,{file_to_base64(bold)}) format('truetype');
      font-weight: 800;
    }}
    """


CUSTOM_CSS = f"""
<style>
{build_font_css()}

* {{
  box-sizing: border-box;
  font-family: 'MusinsaFont', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
  text-align: center;
}}

html, body, .stApp {{
  margin: 0;
  padding: 0;
  background-color: #000 !important;
  color: #fff !important;
  overflow-x: hidden;
}}

[data-testid="stHeader"] {{
  background: transparent;
}}

[data-testid="stToolbar"],
[data-testid="stDecoration"],
#MainMenu,
footer {{
  display: none !important;
}}

.block-container {{
  max-width: 1560px;
  padding-top: 3.4rem;
  padding-bottom: 3.2rem;
}}

.App {{
  min-height: 84vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #000;
}}

.content-wrapper {{
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
}}

.fade-in {{
  animation: fadeIn 0.55s ease-out forwards;
}}

@keyframes fadeIn {{
  from {{ opacity: 0; transform: translateY(10px); }}
  to {{ opacity: 1; transform: translateY(0); }}
}}

/* =========================
   Main
   ========================= */

.top-title {{
  font-size: 1.82rem !important;
  font-weight: 500;
  letter-spacing: 5px;
  color: #fff;
  margin-bottom: 0;
}}

.main-title {{
  font-size: 5.1rem !important;
  color: #fff;
  line-height: 1.02;
  display: flex;
  justify-content: center;
  align-items: center;
  margin: 66px 0 88px 0;
  letter-spacing: 0.05em !important;
}}

.main-title .separator {{
  font-weight: 200 !important;
  margin: 0 36px;
  letter-spacing: normal !important;
}}

.description {{
  font-size: 1.58rem !important;
  font-weight: 500 !important;
  color: #fff;
  word-break: keep-all;
  line-height: 1.86 !important;
  margin-top: 0;
  margin-bottom: 76px;
}}

.description strong {{
  display: block;
  font-weight: 800;
  margin-top: 18px;
}}

/* =========================
   Question
   ========================= */

.progress-shell {{
  width: 100%;
  max-width: 1040px;
  margin: 0 auto 86px auto;
}}

.progress-meta {{
  display: flex;
  justify-content: space-between;
  color: #d1d5db;
  font-size: 1.05rem;
  font-weight: 500;
  margin-bottom: 12px;
}}

.progress-bar-lite {{
  width: 100%;
  height: 4px;
  background-color: #333;
  border-radius: 2px;
  overflow: hidden;
}}

.progress-lite {{
  height: 100%;
  background-color: #fff;
  transition: width 0.3s ease-in-out;
}}

.q-count {{
  font-size: 1.34rem;
  font-weight: 800;
  color: #fff;
  margin: 0 0 32px 0 !important;
  letter-spacing: 0.01em;
}}

.question-text {{
  font-size: 2.24rem;
  font-weight: 500;
  line-height: 1.42;
  margin: 0 0 54px 0;
  color: #fff;
  word-break: keep-all;
}}

/* =========================
   Result
   ========================= */

.result-container-lite {{
  max-width: 820px;
  margin: 120px auto 36px auto;
  padding: 58px 48px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 24px;
  text-align: center;
}}

.result-label {{
  font-size: 1.38rem !important;
  color: #fff;
  margin-bottom: 12px;
}}

.result-title-main {{
  font-size: 3.75rem !important;
  margin: 24px 0;
  font-weight: 800;
  color: #fff;
}}

.persona-desc {{
  font-size: 1.24rem !important;
  line-height: 1.82;
  color: #ccc;
  margin-bottom: 34px;
  word-break: keep-all;
}}

.group-pill {{
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 40px;
  padding: 8px 20px;
  margin: 12px auto 10px;
  background: #fff;
  color: #000;
  border-radius: 999px;
  font-size: 1rem;
  font-weight: 800;
}}

.keyword-pill {{
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 34px;
  padding: 8px 14px;
  background: #fff;
  color: #000;
  border-radius: 999px;
  font-size: 0.92rem;
  font-weight: 800;
  margin: 5px;
}}

/* =========================
   Price
   ========================= */

.price-setting-container-lite {{
  max-width: 720px;
  margin: 70px auto 32px auto;
  padding: 34px 32px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 25px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}}

.price-title {{
  margin-bottom: 12px;
  color: #fff;
  font-size: 2.08rem;
  font-weight: 800;
}}

.price-subtitle {{
  color: #888;
  margin-bottom: 28px;
  font-size: 1rem;
}}

.price-cat-label-lite {{
  width: 100%;
  color: #eee;
  font-weight: 800;
  font-size: 1.04rem;
  text-align: left !important;
  margin: 16px 0 6px 0;
}}

div[data-testid="stNumberInput"] input {{
  background: #222 !important;
  color: #fff !important;
  border: 1px solid #444 !important;
  border-radius: 8px !important;
  text-align: left !important;
  min-height: 44px;
}}

div[data-testid="stNumberInput"] label {{
  color: #fff !important;
  font-size: 0.9rem !important;
}}

/* =========================
   Women snap
   ========================= */

.snap-card {{
  background: #fff;
  color: #000;
  border-radius: 18px;
  overflow: hidden;
  padding: 0 0 12px 0;
  margin-bottom: 12px;
  box-shadow: none;
}}

.snap-card img {{
  border-radius: 18px 18px 0 0;
}}

.snap-card.group-choice {{
  padding-bottom: 0;
  background: transparent;
}}

.snap-card.group-choice img {{
  border-radius: 18px;
}}

.snap-card.group-choice .snap-caption,
.snap-card.group-choice .snap-subcaption {{
  display: none;
}}

.snap-caption {{
  color: #000;
  font-size: 1.05rem;
  font-weight: 800;
  padding-top: 10px;
}}

.snap-subcaption {{
  color: #777;
  font-size: 0.78rem;
  letter-spacing: 0.08em;
  padding-bottom: 2px;
}}

.missing-img {{
  width: 100%;
  aspect-ratio: 3 / 4;
  background: #111;
  color: #666;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid #222;
  border-radius: 18px;
  font-size: 0.8rem;
  word-break: break-all;
  padding: 8px;
}}

/* =========================
   Collage lite
   ========================= */

.advanced-collage-layout-lite {{
  display: flex;
  flex-direction: row;
  width: 100%;
  min-height: 84vh;
  background-color: #000;
  padding: 8px 18px;
  gap: 80px;
  justify-content: center;
  align-items: center;
}}

.left-canvas-area-lite {{
  flex: 0 0 560px;
  display: flex;
  flex-direction: column;
  align-items: center;
}}

.right-list-area-lite {{
  flex: 0 0 680px;
  display: flex;
  flex-direction: column;
  text-align: left;
  max-height: 85vh;
  overflow-y: auto;
  padding-right: 15px;
}}

.right-list-area-lite::-webkit-scrollbar {{
  width: 6px;
}}

.right-list-area-lite::-webkit-scrollbar-thumb {{
  background: #333;
  border-radius: 10px;
}}

.canvas-header-lite {{
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
}}

.instruction {{
  font-size: 0.85rem;
  color: #666;
  margin-bottom: 22px;
}}

.collage-canvas-lite {{
  width: 560px;
  height: 805px;
  border: 1px solid #fff;
  border-radius: 12px;
  position: relative;
  overflow: hidden;
  background-size: cover;
  background-position: center;
  padding: 44px;
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  align-content: center;
  justify-items: center;
  gap: 18px;
}}

.canvas-product-lite {{
  width: 178px;
  height: 178px;
  object-fit: contain;
  filter: drop-shadow(0 4px 8px rgba(0,0,0,0.25));
}}

.sidebar-title {{
  font-size: 1.2rem;
  font-weight: 800;
  color: #fff;
  margin-bottom: 25px;
  letter-spacing: 2px;
  text-align: left !important;
}}

.cat-section-lite {{
  margin-bottom: 24px;
}}

.cat-header-lite {{
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}}

.cat-name {{
  font-size: 0.95rem;
  font-weight: 800;
  color: #fff;
}}

.item-grid-lite {{
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  gap: 10px;
  background: transparent;
}}

.item-card-lite {{
  flex: 0 0 115px;
  display: flex;
  flex-direction: column;
  background-color: #fff;
  border-radius: 12px;
  overflow: hidden;
  padding-bottom: 8px;
}}

.item-card-lite .img-box-lite {{
  width: 115px;
  height: 100px;
  background-color: transparent;
  display: flex;
  align-items: center;
  justify-content: center;
}}

.item-card-lite .img-box-lite img {{
  width: 80%;
  height: 80%;
  object-fit: contain;
}}

.price-text {{
  color: #000 !important;
  font-size: 0.83rem;
  font-weight: 500;
  user-select: none;
  margin: 0;
}}

.product-name-lite {{
  color: #333;
  font-size: 0.68rem;
  line-height: 1.22;
  padding: 2px 6px 4px 6px;
  height: 34px;
  overflow: hidden;
  word-break: keep-all;
}}

.empty-slot-lite {{
  height: 144px;
  align-items: center;
  justify-content: center;
  color: #999;
  font-size: 0.78rem;
}}

hr {{
  border: 0.5px solid #333;
  margin: 20px 0 20px 0 !important;
}}

/* =========================
   Streamlit button tuning
   ========================= */

div.stButton > button {{
  min-height: 68px;
  background-color: #fff !important;
  color: #000 !important;
  border-radius: 12px !important;
  font-size: 1.42rem !important;
  font-weight: 500 !important;
  border: none !important;
  cursor: pointer;
  width: 100%;
  line-height: 1.2;
}}

div.stButton > button:hover {{
  background-color: #e5e5e5 !important;
  color: #000 !important;
  border: none !important;
}}

[data-testid="stAlert"] {{
  background-color: rgba(255,255,255,0.06);
  color: #fff;
  border: 1px solid rgba(255,255,255,0.12);
}}

div[data-testid="stMetric"] {{
  background: rgba(255,255,255,0.04);
  border-radius: 14px;
  padding: 12px;
}}

div[data-testid="stMetricValue"] {{
  color: #fff;
}}

@media (max-width: 1100px) {{
  .block-container {{
    padding-left: 1.2rem;
    padding-right: 1.2rem;
  }}

  .advanced-collage-layout-lite {{
    flex-direction: column;
    align-items: center;
  }}

  .left-canvas-area-lite,
  .right-list-area-lite {{
    flex: 1 1 auto;
    width: 100%;
    max-width: 720px;
  }}

  .collage-canvas-lite {{
    width: 100%;
    height: 720px;
  }}

  .main-title {{
    font-size: 3.1rem !important;
    flex-wrap: wrap;
    margin: 42px 0 56px 0;
  }}

  .description {{
    font-size: 1.25rem !important;
    margin-bottom: 48px;
  }}

  .question-text {{
    font-size: 1.74rem;
  }}
}}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ============================================================
# 2. 원본 data.js 기반 남성 페르소나 데이터
# ============================================================

PERSONAS = [
    "올드머니", "프레피", "미니멀", "시티보이", "오피스룩", "아메카지", "워크웨어",
    "고프코어", "밀리터리", "락시크", "스트릿", "그런지", "Y2K", "블록코어", "애슬레저", "머슬핏"
]

PERSONA_DESCRIPTIONS = {
    "올드머니": "은은하게 드러나는 고급스러움, 절제된 클래식의 정수",
    "프레피": "단정한 학생 스타일의 현대적 재해석",
    "미니멀": "간결한 실루엣과 무채색의 조화",
    "오피스룩": "세련되고 깔끔한 비즈니스 스타일",
    "워크웨어": "거칠고 단단한 소재 속 기능성과 투박한 멋",
    "아메카지": "아메리칸 캐주얼을 일본 특유의 감성으로 재해석한 빈티지 룩",
    "고프코어": "일상 속에 아웃도어를 담은 테크니컬 룩",
    "밀리터리": "군복의 디테일을 활용한 강인한 스타일",
    "락시크": "슬림한 실루엣과 가죽, 블랙 컬러가 주는 일탈",
    "그런지": "정해지지 않은 자유로움, 거친 질감의 빈티지함",
    "스트릿": "자유분방한 거리의 에너지와 힙한 감성",
    "Y2K": "2000년대 초반의 낙천적이고 화려한 세기말 감성",
    "시티보이": "도시의 일상 속 여유로운 실루엣과 편안함",
    "블록코어": "스포츠 유니폼을 일상복으로 활용한 스포티 룩",
    "애슬레저": "운동복과 일상복의 경계를 허문 편안한 스타일",
    "머슬핏": "강인한 신체 라인을 강조하는 역동적인 실루엣",
}

PERSONA_BACK_MAP = {
    "올드머니": "OLDMONEY.png",
    "프레피": "PREPPYLOOK.png",
    "미니멀": "MINIMAL.png",
    "시티보이": "CITYBOY.png",
    "오피스룩": "OFFICELOOK.png",
    "아메카지": "AMEKAJI.png",
    "워크웨어": "WORKWEAR.png",
    "고프코어": "GORPCORE.png",
    "밀리터리": "MILITARYLOOK.png",
    "락시크": "ROCKCHIC.png",
    "스트릿": "STREET.png",
    "그런지": "GRUNGE.png",
    "Y2K": "Y2K.png",
    "블록코어": "BLOKECORE.png",
    "애슬레저": "ATHLEISURE.png",
    "머슬핏": "MUSCLEFIT.png",
}

STEP1_QUESTIONS = [
    {
        "q": "Q1. 평소 옷을 선택할 때 가장 큰 비중을 두는 기준은?",
        "a": [
            {"text": "티 내지 않아도 느껴지는 소재의 품격", "type": "A"},
            {"text": "거칠게 다뤄도 멀쩡한 내구성과 실용성", "type": "B"},
            {"text": "내 개성을 확실히 각인시키는 디자인", "type": "C"},
            {"text": "몸이 편하고 활동하기 좋은 기능성", "type": "D"},
        ],
    },
    {
        "q": "Q2. 사람들에게 비춰지길 원하는 나의 첫인상은?",
        "a": [
            {"text": "깔끔하고 정돈된 예의 바른 모습", "type": "A"},
            {"text": "자기 일에 몰두하는 묵직하고 강한 이미지", "type": "B"},
            {"text": "트렌드에 민감하고 감각적인 분위기", "type": "C"},
            {"text": "에너지가 넘치고 여유로운 모습", "type": "D"},
        ],
    },
    {
        "q": "Q3. 현재 내 옷장을 차지하고 있는 지배적인 색감은?",
        "a": [
            {"text": "네이비나 베이지 같은 차분한 무채색", "type": "A"},
            {"text": "카키나 브라운 계열의 짙은 얼스톤", "type": "B"},
            {"text": "블랙 혹은 확실한 원색의 강렬한 대비", "type": "C"},
            {"text": "화이트와 그레이 중심의 산뜻한 톤", "type": "D"},
        ],
    },
    {
        "q": "Q4. 쇼핑 중 가장 먼저 손이 가는 아이템 종류는?",
        "a": [
            {"text": "실루엣이 잘 잡힌 셔츠 혹은 가죽 로퍼", "type": "A"},
            {"text": "빳빳한 데님 재킷이나 포켓이 많은 바지", "type": "B"},
            {"text": "과감한 그래픽 티셔츠나 한정판 스니커즈", "type": "C"},
            {"text": "가벼운 윈드브레이커 혹은 기능성 의류", "type": "D"},
        ],
    },
]

STEP2_GROUPS = {
    "A": {
        "questions": [
            {"q": "Q5. 선호하는 액세서리 스타일은?", "a": [{"text": "고급 시계", "res": "올드머니"}, {"text": "패턴 양말", "res": "프레피"}, {"text": "액세서리 안 함", "res": "미니멀"}, {"text": "가죽 벨트", "res": "오피스룩"}]},
            {"q": "Q6. 가장 즐겨 입는 상의 종류는?", "a": [{"text": "최고급 니트", "res": "올드머니"}, {"text": "금장 블레이저", "res": "프레피"}, {"text": "무지 셔츠", "res": "미니멀"}, {"text": "정갈한 수트 셔츠", "res": "오피스룩"}]},
            {"q": "Q7. 본인이 지향하는 멋의 방향은?", "a": [{"text": "여유로운 럭셔리", "res": "올드머니"}, {"text": "위트 있는 단정함", "res": "프레피"}, {"text": "본질적인 심플함", "res": "미니멀"}, {"text": "프로의 신뢰감", "res": "오피스룩"}]},
            {"q": "Q8. 주말 시간을 보내는 장소는?", "a": [{"text": "호텔 다이닝", "res": "올드머니"}, {"text": "테니스 코트", "res": "프레피"}, {"text": "조용한 카페", "res": "미니멀"}, {"text": "자기계발 공간", "res": "오피스룩"}]},
        ]
    },
    "B": {
        "questions": [
            {"q": "Q5. 가장 자주 신는 신발 종류는?", "a": [{"text": "가죽 워커", "res": "워크웨어"}, {"text": "빈티지 단화", "res": "아메카지"}, {"text": "트레킹화", "res": "고프코어"}, {"text": "군용 스타일 신발", "res": "밀리터리"}]},
            {"q": "Q6. 옷을 볼 때 집착하는 디테일은?", "a": [{"text": "튼튼한 봉제 마감", "res": "워크웨어"}, {"text": "자연스러운 워싱감", "res": "아메카지"}, {"text": "확실한 방수 기능", "res": "고프코어"}, {"text": "절도 있는 실루엣", "res": "밀리터리"}]},
            {"q": "Q7. 좋아하는 원단이나 소재 느낌은?", "a": [{"text": "묵직한 캔버스", "res": "워크웨어"}, {"text": "오래된 데님", "res": "아메카지"}, {"text": "기능성 나일론", "res": "고프코어"}, {"text": "단단한 코튼", "res": "밀리터리"}]},
            {"q": "Q8. 로망이 있는 취미 생활은?", "a": [{"text": "가구 DIY", "res": "워크웨어"}, {"text": "캠핑 혹은 낚시", "res": "아메카지"}, {"text": "고강도 백패킹", "res": "고프코어"}, {"text": "사격이나 서바이벌", "res": "밀리터리"}]},
        ]
    },
    "C": {
        "questions": [
            {"q": "Q5. 가장 신경 쓰는 포인트 아이템은?", "a": [{"text": "실버 체인", "res": "락시크"}, {"text": "낡은 비니", "res": "그런지"}, {"text": "한정판 신발", "res": "스트릿"}, {"text": "틴트 선글라스", "res": "Y2K"}]},
            {"q": "Q6. 선호하는 바지의 실루엣은?", "a": [{"text": "슬림한 핏", "res": "락시크"}, {"text": "헐렁한 빈티지 핏", "res": "그런지"}, {"text": "넉넉한 카고 핏", "res": "스트릿"}, {"text": "로우라이즈 배기 핏", "res": "Y2K"}]},
            {"q": "Q7. 평소 즐겨 듣는 음악 장르는?", "a": [{"text": "락 혹은 메탈", "res": "락시크"}, {"text": "인디나 얼터너티브", "res": "그런지"}, {"text": "힙합", "res": "스트릿"}, {"text": "일렉트로닉 팝", "res": "Y2K"}]},
            {"q": "Q8. 가보고 싶은 파티나 공간은?", "a": [{"text": "지하 클럽 공연", "res": "락시크"}, {"text": "LP 바", "res": "그런지"}, {"text": "스니커즈 편집숍", "res": "스트릿"}, {"text": "레트로 컨셉 파티", "res": "Y2K"}]},
        ]
    },
    "D": {
        "questions": [
            {"q": "Q5. 항상 챙기는 필수 소지품은?", "a": [{"text": "에코백과 안경", "res": "시티보이"}, {"text": "스포츠 머플러", "res": "블록코어"}, {"text": "스마트 워치", "res": "애슬레저"}, {"text": "단백질 쉐이커", "res": "머슬핏"}]},
            {"q": "Q6. 일상에서 옷을 입는 스타일은?", "a": [{"text": "깔끔함과 편안함의 조합", "res": "시티보이"}, {"text": "유니폼 믹스매치", "res": "블록코어"}, {"text": "활동성 위주의 룩", "res": "애슬레저"}, {"text": "체형 강조형", "res": "머슬핏"}]},
            {"q": "Q7. 닮고 싶은 라이프스타일은?", "a": [{"text": "여유 있는 시티 라이프", "res": "시티보이"}, {"text": "열정적인 스포츠 팬", "res": "블록코어"}, {"text": "세련된 웰니스 라이프", "res": "애슬레저"}, {"text": "완벽한 자기관리", "res": "머슬핏"}]},
            {"q": "Q8. 운동을 지속하는 목적은?", "a": [{"text": "가벼운 산책과 사색", "res": "시티보이"}, {"text": "팀 스포츠의 희열", "res": "블록코어"}, {"text": "컨디션 유지", "res": "애슬레저"}, {"text": "강인한 신체 단련", "res": "머슬핏"}]},
        ]
    },
}


# ============================================================
# 3. 여성 페르소나 데이터
# ============================================================

WOMEN_GROUPS = {
    "A": {"id": "A", "emoji": "🏛️", "label": "클래식 & 엘리트", "en": "Classic & Elite", "personas": ["클래식", "프레피룩", "미니멀"]},
    "B": {"id": "B", "emoji": "🛠️", "label": "실용 & 헤리티지", "en": "Utility & Heritage", "personas": ["워크웨어", "레트로", "고프코어"]},
    "C": {"id": "C", "emoji": "💣", "label": "반항 & 개성", "en": "Rebel & Identity", "personas": ["걸리시", "시크", "스트릿"]},
    "D": {"id": "D", "emoji": "🎾", "label": "스포티 & 캐주얼", "en": "Sporty & Casual", "personas": ["스포티", "캐주얼"]},
}

WOMEN_GROUP_TIE_PRIORITY = ["C", "A", "D", "B"]

WOMEN_PERSONA_DESCRIPTIONS = {
    "클래식": "시간이 지나도 변하지 않는 정돈된 실루엣과 우아한 분위기를 선호합니다.",
    "프레피룩": "셔츠, 니트, 플리츠처럼 단정하면서도 경쾌한 엘리트 캐주얼을 선호합니다.",
    "미니멀": "과한 장식보다 간결한 실루엣과 차분한 컬러를 선호합니다.",
    "워크웨어": "포켓, 데님, 카고처럼 실용적인 디테일이 살아 있는 스타일을 선호합니다.",
    "레트로": "빈티지한 컬러와 패턴, 익숙하지만 개성 있는 무드를 선호합니다.",
    "고프코어": "아웃도어 기반의 기능성 아이템을 일상복으로 즐기는 타입입니다.",
    "걸리시": "스커트, 리본, 밝은 컬러처럼 사랑스럽고 발랄한 분위기를 선호합니다.",
    "시크": "블랙, 슬림한 실루엣, 절제된 디테일로 선명한 인상을 남깁니다.",
    "스트릿": "오버핏, 그래픽, 볼드한 아이템으로 개성을 드러내는 스타일입니다.",
    "스포티": "져지, 트랙팬츠, 스니커즈처럼 활동적이고 에너지 있는 스타일을 선호합니다.",
    "캐주얼": "티셔츠, 데님, 스니커즈처럼 편안하고 자연스러운 데일리룩을 선호합니다.",
}

WOMEN_GROUP_QUESTIONS = [
    {
        "id": i,
        "title": title,
        "options": [
            {"group": "A", "label": "GROUP A", "image": WOMEN_SNAP_DIR / "snap_images_A" / f"A_{i}.jpg"},
            {"group": "B", "label": "GROUP B", "image": WOMEN_SNAP_DIR / "snap_images_B" / f"B_{i}.jpg"},
            {"group": "C", "label": "GROUP C", "image": WOMEN_SNAP_DIR / "snap_images_C" / f"C_{i}.jpg"},
            {"group": "D", "label": "GROUP D", "image": WOMEN_SNAP_DIR / "snap_images_D" / f"D_{i}.jpg"},
        ],
    }
    for i, title in enumerate([
        "가장 마음에 드는 스타일을 골라주세요.",
        "가장 끌리는 분위기의 코디를 선택해주세요.",
        "평소 입어보고 싶은 룩에 가까운 사진을 골라주세요.",
        "가장 나답다고 느껴지는 스타일은 무엇인가요?",
        "주말에 입고 싶은 코디를 선택해주세요.",
        "가장 저장하고 싶은 스냅을 골라주세요.",
        "친구가 추천해줬을 때 가장 입어보고 싶은 룩은?",
        "마지막으로, 가장 오래 보고 싶은 스타일을 선택해주세요.",
    ], start=1)
]

WOMEN_SUBGROUP_QUESTIONS = {
    "A": [
        {"persona": "클래식", "label": "클래식", "image": WOMEN_SUBGROUP_DIR / "A" / "classic.jpg"},
        {"persona": "프레피룩", "label": "프레피룩", "image": WOMEN_SUBGROUP_DIR / "A" / "preppy.jpg"},
        {"persona": "미니멀", "label": "미니멀", "image": WOMEN_SUBGROUP_DIR / "A" / "minimal.jpg"},
        {"persona": "미니멀", "label": "미니멀", "image": WOMEN_SUBGROUP_DIR / "A" / "minimal_alt.jpg"},
    ],
    "B": [
        {"persona": "워크웨어", "label": "워크웨어", "image": WOMEN_SUBGROUP_DIR / "B" / "workwear.jpg"},
        {"persona": "레트로", "label": "레트로", "image": WOMEN_SUBGROUP_DIR / "B" / "retro.jpg"},
        {"persona": "고프코어", "label": "고프코어", "image": WOMEN_SUBGROUP_DIR / "B" / "gorpcore.jpg"},
        {"persona": "고프코어", "label": "고프코어", "image": WOMEN_SUBGROUP_DIR / "B" / "gorpcore_alt.jpg"},
    ],
    "C": [
        {"persona": "걸리시", "label": "걸리시", "image": WOMEN_SUBGROUP_DIR / "C" / "girlish.jpg"},
        {"persona": "시크", "label": "시크", "image": WOMEN_SUBGROUP_DIR / "C" / "chic.jpg"},
        {"persona": "스트릿", "label": "스트릿", "image": WOMEN_SUBGROUP_DIR / "C" / "street.jpg"},
        {"persona": "걸리시", "label": "걸리시", "image": WOMEN_SUBGROUP_DIR / "C" / "girlish_alt.jpg"},
    ],
    "D": [
        {"persona": "스포티", "label": "스포티", "image": WOMEN_SUBGROUP_DIR / "D" / "sporty.jpg"},
        {"persona": "캐주얼", "label": "캐주얼", "image": WOMEN_SUBGROUP_DIR / "D" / "casual.jpg"},
        {"persona": "스포티", "label": "스포티", "image": WOMEN_SUBGROUP_DIR / "D" / "sporty_alt.jpg"},
        {"persona": "캐주얼", "label": "캐주얼", "image": WOMEN_SUBGROUP_DIR / "D" / "casual_alt.jpg"},
    ],
}


# ============================================================
# 4. 추천 데이터 로딩 및 추천 로직
# ============================================================

@st.cache_data(show_spinner=False)
def load_master_data():
    if not MASTER_DATA_PATH.exists():
        return None

    data = np.load(MASTER_DATA_PATH, allow_pickle=True)
    required = ["ids", "names", "prices", "imgs", "cats", "name_vecs", "brand_vecs", "img_vecs", "cat_vecs"]

    missing = [key for key in required if key not in data]
    if missing:
        raise ValueError(f"master_data_lite.npz 키 누락: {missing}")

    master = {}
    for key in required:
        val = data[key]
        if key.endswith("_vecs"):
            if getattr(val, "dtype", None) == object:
                master[key] = np.array([np.array(x, dtype=np.float32) for x in val])
            else:
                master[key] = val.astype(np.float32)
        else:
            master[key] = val

    return master


@st.cache_data(show_spinner=False)
def load_persona_item():
    if not PERSONA_ITEM_PATH.exists():
        return None

    df = pd.read_csv(PERSONA_ITEM_PATH)

    required = {"persona", "outfit", "product_id"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"persona_item_lite.csv 컬럼 누락: {sorted(missing)}")

    return df


def get_price_ranges(master):
    category_map = {
        "outer": "아우터",
        "top": "상의",
        "bottom": "바지",
        "shoes": "신발",
        "acc": "액세서리",
    }

    ranges = {}

    if master is None:
        return {
            "outer": {"min": 0, "max": 300000},
            "top": {"min": 0, "max": 150000},
            "bottom": {"min": 0, "max": 150000},
            "shoes": {"min": 0, "max": 250000},
            "acc": {"min": 0, "max": 100000},
        }

    for eng_key, kor_val in category_map.items():
        mask = master["cats"] == kor_val
        prices = master["prices"][mask]

        if len(prices) > 0:
            ranges[eng_key] = {"min": int(np.min(prices)), "max": int(np.max(prices))}
        else:
            ranges[eng_key] = {"min": 0, "max": 0}

    return ranges


def recommend_products(persona, budget=None, gender=None, top_n=5):
    master = load_master_data()
    persona_item = load_persona_item()

    if master is None or persona_item is None:
        return {
            "ok": False,
            "message": "추천용 lite 데이터가 없습니다. data/lite/master_data_lite.npz와 data/lite/persona_item_lite.csv를 먼저 만들어주세요.",
            "items": {},
        }

    df = persona_item.copy()

    if gender and "gender" in df.columns:
        df = df[df["gender"] == gender]

    outfits = df[df["persona"] == persona]["outfit"].dropna().unique().tolist()
    if not outfits:
        return {
            "ok": False,
            "message": f"persona_item_lite.csv에 '{persona}' 페르소나의 outfit 데이터가 없습니다.",
            "items": {},
        }

    selected_outfit = int(random.choice(outfits))
    target_ids = df[(df["persona"] == persona) & (df["outfit"] == selected_outfit)]["product_id"].tolist()

    ids = master["ids"]
    target_indices = np.where(np.isin(ids, target_ids))[0]
    if len(target_indices) == 0:
        return {
            "ok": False,
            "message": "persona_item_lite.csv의 product_id가 master_data_lite.npz의 ids에 없습니다.",
            "items": {},
        }

    target_item_map = {master["cats"][idx]: idx for idx in target_indices}

    category_map = {
        "outer": "아우터",
        "top": "상의",
        "bottom": "바지",
        "shoes": "신발",
        "acc": "액세서리",
    }

    budget = budget or {}
    final_items = {}

    for eng_key, kor_val in category_map.items():
        if kor_val not in target_item_map:
            final_items[eng_key] = []
            continue

        target_idx = target_item_map[kor_val]

        sim_name = np.dot(master["name_vecs"], master["name_vecs"][target_idx])
        sim_brand = np.dot(master["brand_vecs"], master["brand_vecs"][target_idx])
        sim_img = np.dot(master["img_vecs"], master["img_vecs"][target_idx])
        sim_cat = np.dot(master["cat_vecs"], master["cat_vecs"][target_idx])

        final_scores = (sim_name * 0.1) + (sim_brand * 0.1) + (sim_img * 0.6) + (sim_cat * 0.1)

        price_mask = np.ones(len(master["prices"]), dtype=bool)
        min_price = budget.get(eng_key, {}).get("min")
        max_price = budget.get(eng_key, {}).get("max")

        if min_price is not None:
            price_mask &= master["prices"] >= min_price
        if max_price is not None:
            price_mask &= master["prices"] <= max_price

        combined_mask = (master["cats"] == kor_val) & price_mask
        cat_scores = final_scores[combined_mask]
        cat_real_indices = np.where(combined_mask)[0]

        if len(cat_scores) == 0:
            final_items[eng_key] = []
            continue

        sorted_indices = np.argsort(cat_scores)[::-1][:100]
        sample_count = min(top_n, len(sorted_indices))
        selected_local = np.random.choice(sorted_indices, sample_count, replace=False)

        items = []
        for loc_idx in selected_local:
            original_idx = cat_real_indices[loc_idx]
            items.append({
                "product_id": int(master["ids"][original_idx]),
                "product_name": str(master["names"][original_idx]),
                "price": int(master["prices"][original_idx]),
                "img_url": str(master["imgs"][original_idx]),
                "category": kor_val,
                "score": float(cat_scores[loc_idx]),
            })

        final_items[eng_key] = items

    return {
        "ok": True,
        "persona": persona,
        "outfit": selected_outfit,
        "items": final_items,
    }


# ============================================================
# 5. 상태 및 공통 UI 함수
# ============================================================

def init_state():
    defaults = {
        "page": "main",
        "gender": None,

        "current_idx": 0,
        "history": [],
        "type_scores": {"A": 0, "B": 0, "C": 0, "D": 0},
        "persona_scores": {},
        "selected_type": None,
        "result": "",

        "women_group_answers": [],
        "women_group_result": None,
        "women_final_result": None,

        "budget": {},
        "recommended": None,
        "selected_items": {},
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def rerun():
    st.rerun()


def go(page):
    st.session_state.page = page
    rerun()


def reset_all():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    init_state()
    st.session_state.page = "main"
    rerun()


def centered_button(label, key, on_click=None):
    c1, c2, c3 = st.columns([1, 2.2, 1])
    with c2:
        clicked = st.button(label, key=key, use_container_width=True)
    if clicked and on_click:
        on_click()
    return clicked


def progress_bar(current, total):
    pct = min(max(current / total, 0), 1) * 100
    st.markdown(
        f"""
        <div class="progress-shell">
          <div class="progress-meta">
            <span>{current}</span>
            <span>{total}</span>
          </div>
          <div class="progress-bar-lite">
            <div class="progress-lite" style="width:{pct}%;"></div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_image(path: Path, ratio="3/4"):
    if path.exists():
        st.image(str(path), use_container_width=True)
    else:
        st.markdown(
            f"<div class='missing-img' style='aspect-ratio:{ratio};'>이미지 없음<br>{html.escape(path.as_posix())}</div>",
            unsafe_allow_html=True,
        )


def format_price(value):
    try:
        return f"{int(value):,}원"
    except Exception:
        return "-"


def get_background_src(persona):
    filename = PERSONA_BACK_MAP.get(persona)
    if not filename:
        return None
    return local_image_src(BACKGROUND_DIR / filename)


def item_img_src(url_or_path):
    if not url_or_path:
        return ""
    value = str(url_or_path)
    if value.startswith("http://") or value.startswith("https://") or value.startswith("data:"):
        return value
    path = Path(value)
    if path.exists():
        return local_image_src(path) or ""
    return value


def get_first_selected_items(items_by_category):
    selected = {}
    for cat, items in items_by_category.items():
        if items:
            selected[cat] = items[0]
    return selected


init_state()


# ============================================================
# 6. 점수 계산
# ============================================================

def get_top_type_with_react_rule(scores):
    # JS Object.keys({A,B,C,D}).reduce((a,b)=>scores[a] >= scores[b] ? a : b)
    keys = ["A", "B", "C", "D"]
    top = keys[0]
    for key in keys[1:]:
        if scores[top] < scores[key]:
            top = key
    return top


def get_top_persona_with_react_rule(scores):
    # JS Object.keys(newPersonaScores)의 삽입 순서 기반 tie 처리에 가깝게 구현
    if not scores:
        return ""
    top = list(scores.keys())[0]
    for key in list(scores.keys())[1:]:
        if scores[top] < scores[key]:
            top = key
    return top


def calculate_women_group(answers):
    scores = {"A": 0, "B": 0, "C": 0, "D": 0}
    for answer in answers:
        group = answer.get("group")
        if group in scores:
            scores[group] += 1

    top_group = sorted(
        scores.keys(),
        key=lambda key: (-scores[key], WOMEN_GROUP_TIE_PRIORITY.index(key))
    )[0]

    return {
        "group": top_group,
        "scores": scores,
        "info": WOMEN_GROUPS[top_group],
    }


# ============================================================
# 7. 페이지 렌더링
# ============================================================

def render_main():
    st.markdown(
        """
        <div class="App fade-in">
          <div class="content-wrapper">
            <h2 class="top-title">패션 페르소나 찾기</h2>
            <h1 class="main-title">
              <span class="brand">MUSINSA</span>
              <span class="separator"> X </span>
              <span class="brand">PERSONA</span>
            </h1>
            <div class="description">
              <p>총 8가지 문항으로 옷장 속 숨겨진 당신의</p>
              <p><strong>패션 페르소나를 찾아보세요</strong></p>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    centered_button(
        "남성 텍스트 페르소나 검사하기",
        "main_men_start",
        lambda: start_men_test(),
    )

    centered_button(
        "여성 스냅 페르소나 검사하기",
        "main_women_start",
        lambda: start_women_test(),
    )

    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1, 2.2, 1])
    with c2:
        master_exists = MASTER_DATA_PATH.exists()
        persona_exists = PERSONA_ITEM_PATH.exists()
        if not master_exists or not persona_exists:
            st.info("현재 버전은 페르소나 검사는 바로 가능하고, 실제 상품 추천은 data/lite 데이터가 준비되면 작동합니다.")


def start_men_test():
    st.session_state.gender = "men"
    st.session_state.page = "step1"
    st.session_state.current_idx = 0
    st.session_state.history = []
    st.session_state.type_scores = {"A": 0, "B": 0, "C": 0, "D": 0}
    st.session_state.persona_scores = {}
    st.session_state.selected_type = None
    st.session_state.result = ""
    rerun()


def start_women_test():
    st.session_state.gender = "women"
    st.session_state.page = "women_group_test"
    st.session_state.women_group_answers = []
    st.session_state.women_group_result = None
    st.session_state.women_final_result = None
    st.session_state.result = ""
    rerun()


def render_men_question():
    step = st.session_state.page
    idx = st.session_state.current_idx

    if step == "step1":
        question = STEP1_QUESTIONS[idx]
        current_no = idx + 1
        total_no = 8
        answers = question["a"]
    else:
        selected_type = st.session_state.selected_type
        question = STEP2_GROUPS[selected_type]["questions"][idx]
        current_no = idx + 5
        total_no = 8
        answers = question["a"]

    st.markdown("<div class='content-wrapper fade-in' style='max-width:760px;margin:0 auto;'>", unsafe_allow_html=True)
    progress_bar(current_no, total_no)
    st.markdown(f"<p class='q-count'>Q. {current_no} / 8</p>", unsafe_allow_html=True)
    st.markdown(f"<h2 class='question-text'>{html.escape(question['q'])}</h2>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    for i, answer in enumerate(answers):
        centered_button(
            answer["text"],
            f"{step}_{idx}_{i}_{answer['text']}",
            lambda a=answer: handle_men_answer(a),
        )

    centered_button("이전 질문으로", f"{step}_{idx}_back", go_men_back)


def handle_men_answer(answer):
    step = st.session_state.page
    idx = st.session_state.current_idx

    st.session_state.history.append({
        "type_scores": st.session_state.type_scores.copy(),
        "persona_scores": st.session_state.persona_scores.copy(),
        "current_idx": idx,
        "selected_type": st.session_state.selected_type,
        "page": step,
    })

    if step == "step1":
        new_scores = st.session_state.type_scores.copy()
        new_scores[answer["type"]] += 1
        st.session_state.type_scores = new_scores

        if idx + 1 < len(STEP1_QUESTIONS):
            st.session_state.current_idx += 1
        else:
            final_type = get_top_type_with_react_rule(new_scores)
            st.session_state.selected_type = final_type
            st.session_state.current_idx = 0
            st.session_state.page = "step2"

    elif step == "step2":
        target_persona = answer["res"]
        new_scores = st.session_state.persona_scores.copy()
        new_scores[target_persona] = new_scores.get(target_persona, 0) + 1
        st.session_state.persona_scores = new_scores

        selected_type = st.session_state.selected_type
        current_group_questions = STEP2_GROUPS[selected_type]["questions"]

        if idx + 1 < len(current_group_questions):
            st.session_state.current_idx += 1
        else:
            final_result = get_top_persona_with_react_rule(new_scores)
            st.session_state.result = final_result
            st.session_state.page = "result"

    rerun()


def go_men_back():
    if not st.session_state.history:
        st.session_state.page = "main"
        rerun()

    last = st.session_state.history.pop()
    st.session_state.type_scores = last["type_scores"]
    st.session_state.persona_scores = last["persona_scores"]
    st.session_state.current_idx = last["current_idx"]
    st.session_state.selected_type = last["selected_type"]
    st.session_state.page = last["page"]
    rerun()


def render_men_result():
    result = st.session_state.result
    desc = PERSONA_DESCRIPTIONS.get(result, "")

    st.markdown(
        f"""
        <div class="result-container-lite fade-in">
          <p class="result-label">당신의 페르소나는</p>
          <h1 class="result-title-main">{html.escape(result)}</h1>
          <p class="persona-desc">{html.escape(desc)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    centered_button("확인", "men_result_confirm", lambda: go("price_setting"))
    centered_button("다시하기", "men_result_retry", reset_all)
    centered_button("모든 페르소나 설명 보기", "men_result_desc", lambda: go("descriptions"))


def render_descriptions():
    st.markdown("<h2 class='price-title'>페르소나 가이드</h2>", unsafe_allow_html=True)

    rows = [PERSONAS[i:i + 4] for i in range(0, len(PERSONAS), 4)]
    for row in rows:
        cols = st.columns(4, gap="medium")
        for col, name in zip(cols, row):
            with col:
                desc = PERSONA_DESCRIPTIONS.get(name, "")
                st.markdown(
                    f"""
                    <div style="background:#fff;color:#000;border-radius:12px;width:100%;height:140px;
                                display:flex;flex-direction:column;justify-content:center;align-items:center;
                                padding:12px;margin-bottom:18px;">
                      <strong style="font-size:1.25rem;font-weight:800;color:#000;">{html.escape(name)}</strong>
                      <p style="font-size:0.95rem;line-height:1.35;color:#333;margin:8px 0 0 0;word-break:keep-all;">
                        {html.escape(desc)}
                      </p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    centered_button("결과로 돌아가기", "desc_back", lambda: go("result"))


def render_women_group_test():
    idx = len(st.session_state.women_group_answers)

    if idx >= len(WOMEN_GROUP_QUESTIONS):
        st.session_state.women_group_result = calculate_women_group(st.session_state.women_group_answers)
        st.session_state.page = "women_group_result"
        rerun()

    question = WOMEN_GROUP_QUESTIONS[idx]

    st.markdown("<div class='content-wrapper fade-in' style='max-width:1040px;margin:0 auto;'>", unsafe_allow_html=True)
    progress_bar(idx + 1, len(WOMEN_GROUP_QUESTIONS))
    st.markdown(f"<p class='q-count'>QUESTION {str(idx + 1).zfill(2)}</p>", unsafe_allow_html=True)
    st.markdown(f"<h2 class='question-text'>{html.escape(question['title'])}</h2>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    cols = st.columns(4, gap="medium")
    for i, option in enumerate(question["options"]):
        group_info = WOMEN_GROUPS[option["group"]]
        with cols[i]:
            st.markdown("<div class='snap-card group-choice'>", unsafe_allow_html=True)
            render_image(option["image"])
            st.markdown(
                f"""
                <div class="snap-caption">{group_info['emoji']} {option['label']}</div>
                <div class="snap-subcaption">{html.escape(group_info['label'])}</div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown("</div>", unsafe_allow_html=True)

            if st.button("선택", key=f"women_group_{idx}_{i}", use_container_width=True):
                st.session_state.women_group_answers.append(option)
                rerun()

    centered_button("이전으로", f"women_group_back_{idx}", go_women_group_back)


def go_women_group_back():
    if st.session_state.women_group_answers:
        st.session_state.women_group_answers.pop()
        rerun()
    else:
        st.session_state.page = "main"
        rerun()


def render_women_group_result():
    group_result = st.session_state.women_group_result
    if not group_result:
        go("women_group_test")

    group = group_result["info"]
    personas = " / ".join(group["personas"])

    st.markdown(
        f"""
        <div class="result-container-lite fade-in">
          <p class="result-label">당신의 여성복 스타일 그룹은</p>
          <div class="group-pill">{group['emoji']} GROUP {group['id']}</div>
          <h1 class="result-title-main">{html.escape(group['label'])}</h1>
          <p class="persona-desc">{html.escape(group['en'])}<br>{html.escape(personas)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    score_cols = st.columns(4)
    for col, group_id in zip(score_cols, ["A", "B", "C", "D"]):
        with col:
            st.metric(f"GROUP {group_id}", group_result["scores"].get(group_id, 0))

    st.info("동점일 경우 대그룹 우선순위는 C > A > D > B 입니다.")

    centered_button("세부 페르소나 찾기", "women_go_sub", lambda: go("women_subgroup_test"))
    centered_button("이전 질문으로", "women_group_result_back", go_women_group_back)
    centered_button("처음으로", "women_group_result_home", reset_all)


def render_women_subgroup_test():
    group_result = st.session_state.women_group_result
    if not group_result:
        go("women_group_test")

    group_id = group_result["group"]
    group = group_result["info"]
    options = WOMEN_SUBGROUP_QUESTIONS[group_id]

    st.markdown("<div class='content-wrapper fade-in' style='max-width:760px;margin:0 auto;'>", unsafe_allow_html=True)
    st.markdown(f"<p class='top-title'>GROUP {group_id} · {html.escape(group['label'])}</p>", unsafe_allow_html=True)
    st.markdown("<h1 class='main-title' style='font-size:3rem !important;'>마지막으로 하나만<br>더 골라주세요</h1>", unsafe_allow_html=True)
    st.markdown("<div class='description'><strong>세부 여성복 페르소나를 찾습니다.</strong></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    cols = st.columns(2, gap="large")
    for i, option in enumerate(options):
        with cols[i % 2]:
            st.markdown("<div class='snap-card group-choice'>", unsafe_allow_html=True)
            render_image(option["image"])
            st.markdown(
                f"""
                <div class="snap-caption">{html.escape(option['label'])}</div>
                <div class="snap-subcaption">GROUP {group_id}</div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown("</div>", unsafe_allow_html=True)

            if st.button("선택", key=f"women_sub_{group_id}_{i}", use_container_width=True):
                final = {
                    "gender": "women",
                    "group": group_id,
                    "group_info": group,
                    "group_scores": group_result["scores"],
                    "persona": option["persona"],
                    "description": WOMEN_PERSONA_DESCRIPTIONS.get(option["persona"], ""),
                    "subgroup_answer": option,
                }
                st.session_state.women_final_result = final
                st.session_state.result = option["persona"]
                st.session_state.page = "women_result"
                rerun()

    centered_button("그룹 결과로 돌아가기", "women_sub_back", lambda: go("women_group_result"))


def render_women_result():
    final = st.session_state.women_final_result
    if not final:
        go("women_group_test")

    group = final["group_info"]
    persona = final["persona"]
    desc = final["description"]

    st.markdown(
        f"""
        <div class="result-container-lite fade-in">
          <p class="result-label">당신의 여성복 페르소나는</p>
          <div class="group-pill">{group['emoji']} GROUP {group['id']} · {html.escape(group['label'])}</div>
          <h1 class="result-title-main">{html.escape(persona)}</h1>
          <p class="persona-desc">{html.escape(desc)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    centered_button("추천 코디 보러가기", "women_result_confirm", lambda: go("price_setting"))
    centered_button("다시 검사하기", "women_result_retry", start_women_test)
    centered_button("처음으로 돌아가기", "women_result_home", reset_all)


def render_price_setting():
    persona = st.session_state.result
    if not persona:
        go("main")

    master = load_master_data()
    ranges = get_price_ranges(master)

    category_labels = {
        "outer": "아우터",
        "top": "상의",
        "bottom": "하의",
        "shoes": "신발",
        "acc": "액세서리",
    }

    st.markdown(
        f"""
        <div class="price-setting-container-lite fade-in">
          <h2 class="price-title">예산 설정</h2>
          <p class="price-subtitle">각 카테고리별로 원하는 가격대를 입력해주세요.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    budget = {}
    c1, c2, c3 = st.columns([1, 2.6, 1])

    with c2:
        for cat, label in category_labels.items():
            r = ranges.get(cat, {"min": 0, "max": 300000})
            min_bound = int(r.get("min", 0))
            max_bound = int(r.get("max", 300000))
            if max_bound <= 0:
                max_bound = 300000

            st.markdown(f"<div class='price-cat-label-lite'>{label}</div>", unsafe_allow_html=True)

            col_min, col_max = st.columns(2)
            with col_min:
                min_price = st.number_input(
                    f"{label} 최소",
                    min_value=0,
                    max_value=max(max_bound * 2, 1),
                    value=min_bound,
                    step=5000,
                    key=f"min_{cat}",
                )
            with col_max:
                max_price = st.number_input(
                    f"{label} 최대",
                    min_value=0,
                    max_value=max(max_bound * 2, 1),
                    value=max_bound,
                    step=5000,
                    key=f"max_{cat}",
                )

            if min_price > max_price:
                st.error("최소 가격이 최대 가격보다 클 수 없습니다.")

            budget[cat] = {"min": int(min_price), "max": int(max_price)}

    st.session_state.budget = budget

    centered_button("추천 상품 확인하기", "price_submit", run_recommendation)
    centered_button("다시하기", "price_reset", reset_all)


def run_recommendation():
    with st.spinner("분석 중..."):
        st.session_state.recommended = recommend_products(
            persona=st.session_state.result,
            budget=st.session_state.budget,
            gender=st.session_state.gender,
            top_n=5,
        )
    st.session_state.page = "collage"
    rerun()


def render_collage():
    rec = st.session_state.recommended
    persona = st.session_state.result

    if not rec:
        go("price_setting")

    if not rec.get("ok"):
        st.error(rec.get("message", "추천 결과를 만들 수 없습니다."))
        centered_button("예산 설정으로 돌아가기", "rec_back_budget", lambda: go("price_setting"))
        centered_button("처음으로", "rec_home", reset_all)
        return

    items_by_category = rec.get("items", {})
    selected_items = get_first_selected_items(items_by_category)
    st.session_state.selected_items = selected_items

    bg_src = get_background_src(persona)
    bg_style = f"background-image:url('{bg_src}');" if bg_src else "background:#050505;"

    canvas_imgs = ""
    for cat in ["outer", "top", "bottom", "shoes", "acc"]:
        item = selected_items.get(cat)
        if not item:
            continue
        src = html.escape(item_img_src(item.get("img_url", "")))
        canvas_imgs += f"<img class='canvas-product-lite' src='{src}' alt=''>"

    st.markdown(
        f"""
        <div class="advanced-collage-layout-lite fade-in">
          <section class="left-canvas-area-lite">
            <div class="canvas-header-lite">
              <p class="instruction">포트폴리오 Lite 버전: 추천 상품을 코디 보드 형태로 표시합니다.</p>
            </div>
            <div class="collage-canvas-lite" style="{bg_style}">
              {canvas_imgs}
            </div>
          </section>
          <section class="right-list-area-lite">
            <h2 class="sidebar-title">{html.escape(persona)} 스타일 추천</h2>
        """,
        unsafe_allow_html=True,
    )

    category_order = ["outer", "top", "bottom", "shoes", "acc"]
    category_labels = {
        "outer": "OUTER",
        "top": "TOP",
        "bottom": "BOTTOM",
        "shoes": "SHOES",
        "acc": "ACC",
    }

    for cat in category_order:
        items = items_by_category.get(cat, [])

        st.markdown(
            f"""
            <div class="cat-section-lite">
              <div class="cat-header-lite">
                <span class="cat-name">{category_labels[cat]}</span>
              </div>
              <div class="item-grid-lite">
            """,
            unsafe_allow_html=True,
        )

        cards = ""
        for i in range(5):
            if i < len(items):
                item = items[i]
                img = html.escape(item_img_src(item.get("img_url", "")))
                name = html.escape(str(item.get("product_name", "")))
                price = format_price(item.get("price"))
                cards += f"""
                <div class="item-card-lite">
                  <div class="img-box-lite"><img src="{img}" alt=""></div>
                  <div class="product-name-lite">{name}</div>
                  <p class="price-text">{price}</p>
                </div>
                """
            else:
                cards += """
                <div class="item-card-lite empty-slot-lite">
                  해당 상품 없음
                </div>
                """

        st.markdown(cards + "</div></div>", unsafe_allow_html=True)

    st.markdown("</section></div>", unsafe_allow_html=True)

    centered_button("다른 추천 보기", "shuffle_all", run_recommendation)
    centered_button("이전으로", "collage_back", lambda: go("price_setting"))
    centered_button("메인으로", "collage_home", reset_all)


# ============================================================
# 8. 라우팅
# ============================================================

page = st.session_state.page

if page == "main":
    render_main()
elif page in ["step1", "step2"]:
    render_men_question()
elif page == "result":
    render_men_result()
elif page == "descriptions":
    render_descriptions()
elif page == "women_group_test":
    render_women_group_test()
elif page == "women_group_result":
    render_women_group_result()
elif page == "women_subgroup_test":
    render_women_subgroup_test()
elif page == "women_result":
    render_women_result()
elif page == "price_setting":
    render_price_setting()
elif page == "collage":
    render_collage()
else:
    reset_all()
