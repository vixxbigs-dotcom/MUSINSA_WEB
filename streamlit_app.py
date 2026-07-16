import base64
import html
import json
import random
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from services.lite_recommender import (
    get_price_ranges as get_lite_price_ranges,
    recommend_products as recommend_lite_products,
)


# ============================================================
# MUSINSA PERSONA LITE
# React 원본 구조 + 남성 벡터 추천 + 여성 MD 스냅 큐레이션 Lite 버전
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
PROCESSED_IMAGE_DIR = BASE_DIR / "data" / "lite" / "processed_imgs"
EXCLUDED_PRODUCT_PATH = BASE_DIR / "data" / "lite" / "excluded_product_ids.csv"


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

/* ==========================================================
   UI V2 overrides - MUSINSA x Apple minimal direction
   ========================================================== */

/* Main: remove the oversized hero height that created the empty gap */
.App {{
  min-height: auto;
  padding: clamp(54px, 8vh, 96px) 0 18px;
}}

.main-title {{
  margin-top: 48px;
  margin-bottom: 58px;
}}

.description {{
  margin-bottom: 18px;
}}

section[data-testid="stMain"]:has(.main-page-marker) .block-container {{
  max-width: 1180px;
  padding-top: 1rem;
}}

section[data-testid="stMain"]:has(.main-page-marker) button[kind="primary"] {{
  min-height: 66px;
  background: #fff !important;
  color: #050505 !important;
  border: 0 !important;
  border-radius: 12px !important;
  font-size: 19px !important;
  font-weight: 800 !important;
}}

section[data-testid="stMain"]:has(.main-page-marker) button[kind="primary"] p {{
  font-size: 19px !important;
  font-weight: 800 !important;
}}

/* Link-style actions: previous question / guide navigation */
button[kind="tertiary"] {{
  min-height: 30px !important;
  padding: 2px 8px !important;
  background: transparent !important;
  color: #b8b8b8 !important;
  border: 0 !important;
  border-radius: 0 !important;
  box-shadow: none !important;
  text-decoration: underline !important;
  text-underline-offset: 4px;
  font-size: 14px !important;
  font-weight: 500 !important;
}}

button[kind="tertiary"] p {{
  color: inherit !important;
  font-size: inherit !important;
  font-weight: inherit !important;
  text-decoration: underline !important;
  text-underline-offset: 4px;
}}

button[kind="tertiary"]:hover {{
  background: transparent !important;
  color: #fff !important;
}}

/* Result card */
div[data-testid="stVerticalBlockBorderWrapper"]:has(.result-page-marker) {{
  width: min(700px, calc(100vw - 40px));
  margin: clamp(54px, 12vh, 125px) auto 0;
  padding: 46px 34px 34px;
  background: #111 !important;
  border: 0 !important;
  border-radius: 20px !important;
  box-shadow: none !important;
}}

div[data-testid="stVerticalBlockBorderWrapper"]:has(.result-page-marker) [data-testid="stVerticalBlock"] {{
  gap: 0.72rem;
}}

.result-card-copy {{
  padding: 2px 0 22px;
}}

.result-card-label {{
  margin: 0 0 8px;
  color: #f4f4f4;
  font-size: 20px;
  font-weight: 500;
}}

.result-card-title {{
  margin: 0;
  color: #fff;
  font-size: clamp(44px, 4vw, 58px);
  line-height: 1.08;
  font-weight: 800;
  letter-spacing: -0.035em;
}}

.result-card-desc {{
  margin: 22px 0 0;
  color: #aaa;
  font-size: 17px;
  line-height: 1.55;
  word-break: keep-all;
}}

div[data-testid="stVerticalBlockBorderWrapper"]:has(.result-page-marker) button[kind="secondary"] {{
  min-height: 54px;
  border-radius: 10px !important;
  font-size: 19px !important;
  font-weight: 800 !important;
}}

div[data-testid="stVerticalBlockBorderWrapper"]:has(.result-page-marker) button[kind="secondary"] p {{
  font-size: 19px !important;
  font-weight: 800 !important;
}}

/* Persona guide */
section[data-testid="stMain"]:has(.guide-page-marker) .block-container {{
  max-width: 760px;
  padding-top: 2.4rem;
  padding-bottom: 2.2rem;
}}

.guide-page-title {{
  margin: 0 0 54px;
  color: #fff;
  font-size: 25px;
  font-weight: 800;
}}

.persona-guide-grid {{
  width: min(520px, 100%);
  margin: 0 auto 42px;
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
}}

.persona-guide-card {{
  min-height: 120px;
  padding: 16px 10px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: #fff;
  color: #050505;
  border-radius: 10px;
}}

.persona-guide-name {{
  color: #050505;
  font-size: 19px;
  line-height: 1.15;
  font-weight: 800;
  letter-spacing: -0.025em;
}}

.persona-guide-desc {{
  margin: 8px 0 0;
  color: #333;
  font-size: 12px;
  line-height: 1.42;
  font-weight: 500;
  word-break: keep-all;
}}

/* Budget card */
div[data-testid="stVerticalBlockBorderWrapper"]:has(.price-page-marker) {{
  width: min(620px, calc(100vw - 40px));
  margin: clamp(40px, 8vh, 76px) auto 0;
  padding: 34px 26px 28px;
  background: #111 !important;
  border: 1px solid #303030 !important;
  border-radius: 20px !important;
  box-shadow: none !important;
}}

.price-card-head {{
  margin-bottom: 16px;
}}

.price-card-head h2 {{
  margin: 0;
  color: #fff;
  font-size: 24px;
  font-weight: 800;
}}

.price-card-head p {{
  margin: 10px 0 0;
  color: #8f8f8f;
  font-size: 14px;
  font-weight: 500;
}}

div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stVerticalBlockBorderWrapper"]:has(.budget-row-marker) {{
  margin: 0 0 10px;
  padding: 9px 12px;
  background: #090909 !important;
  border: 0 !important;
  border-radius: 10px !important;
}}

div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stVerticalBlockBorderWrapper"]:has(.budget-row-marker) [data-testid="stHorizontalBlock"] {{
  align-items: center;
}}

.budget-label {{
  width: 100%;
  color: #f3f3f3;
  font-size: 14px;
  line-height: 40px;
  font-weight: 800;
  text-align: left !important;
}}

.budget-separator {{
  color: #777;
  font-size: 13px;
  line-height: 40px;
}}

div[data-testid="stVerticalBlockBorderWrapper"]:has(.price-page-marker) div[data-testid="stTextInput"] {{
  margin: 0;
}}

div[data-testid="stVerticalBlockBorderWrapper"]:has(.price-page-marker) div[data-testid="stTextInput"] input {{
  min-height: 40px;
  padding: 0 13px;
  background: #242424 !important;
  color: #e7e7e7 !important;
  border: 1px solid #3c3c3c !important;
  border-radius: 7px !important;
  text-align: left !important;
  font-size: 13px !important;
  font-weight: 500 !important;
  box-shadow: none !important;
}}

div[data-testid="stVerticalBlockBorderWrapper"]:has(.price-page-marker) button[kind="secondary"] {{
  min-height: 54px;
  margin-top: 10px;
  border-radius: 10px !important;
  font-size: 18px !important;
  font-weight: 800 !important;
}}

div[data-testid="stVerticalBlockBorderWrapper"]:has(.price-page-marker) button[kind="secondary"] p {{
  font-size: 18px !important;
  font-weight: 800 !important;
}}

/* Collage */
section[data-testid="stMain"]:has(.collage-page-marker) .block-container {{
  max-width: 1120px;
  padding-top: 1.4rem;
  padding-bottom: 1.2rem;
}}

.collage-left-shell {{
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  padding-top: 2px;
}}

.collage-canvas-v2 {{
  width: min(390px, 100%);
  aspect-ratio: 0.72;
  position: relative;
  overflow: hidden;
  background-size: cover;
  background-position: center;
  border: 1px solid #9ca3af;
  border-radius: 11px;
  box-shadow: none;
}}

.collage-canvas-v2::after {{
  content: "";
  position: absolute;
  inset: 8px;
  border: 1px solid rgba(255,255,255,0.75);
  border-radius: 9px;
  pointer-events: none;
}}

.collage-canvas-v2 .canvas-product-v2 {{
  position: absolute;
  width: 38%;
  height: 34%;
  object-fit: contain;
  filter: drop-shadow(0 5px 8px rgba(0,0,0,0.18));
  z-index: 2;
}}

.collage-canvas-v2 .canvas-product-v2:nth-child(1) {{ left: 7%; top: 18%; width: 43%; height: 48%; }}
.collage-canvas-v2 .canvas-product-v2:nth-child(2) {{ right: 8%; top: 16%; width: 44%; height: 36%; }}
.collage-canvas-v2 .canvas-product-v2:nth-child(3) {{ right: 10%; bottom: 7%; width: 39%; height: 44%; }}
.collage-canvas-v2 .canvas-product-v2:nth-child(4) {{ left: 7%; bottom: 7%; width: 37%; height: 24%; }}
.collage-canvas-v2 .canvas-product-v2:nth-child(5) {{ left: 44%; top: 22%; width: 18%; height: 24%; }}

.collage-right-shell {{
  max-height: 545px;
  overflow-y: auto;
  padding-right: 8px;
}}

.collage-right-shell::-webkit-scrollbar {{
  width: 5px;
}}

.collage-right-shell::-webkit-scrollbar-thumb {{
  background: #333;
  border-radius: 999px;
}}

.collage-section-v2 {{
  margin-bottom: 16px;
}}

.collage-category-head {{
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}}

.collage-category-name {{
  color: #fff;
  font-size: 12px;
  font-weight: 800;
  text-align: left !important;
}}

.shuffle-chip {{
  min-width: 48px;
  padding: 4px 10px;
  color: #bdbdbd;
  background: #262626;
  border: 1px solid #353535;
  border-radius: 5px;
  font-size: 10px;
  line-height: 1;
}}

.collage-item-grid-v2 {{
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 10px;
}}

.collage-item-card-v2 {{
  min-width: 0;
  height: 104px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: space-between;
  padding: 8px 5px 9px;
  overflow: hidden;
  background: #fff;
  border-radius: 9px;
}}

.collage-item-card-v2 img {{
  width: 82%;
  height: 72px;
  object-fit: contain;
}}

.collage-item-price-v2 {{
  margin: 0;
  color: #050505;
  font-size: 10px;
  line-height: 1;
  font-weight: 500;
}}

.collage-empty-v2 {{
  justify-content: center;
  color: #8b8b8b;
  font-size: 10px;
}}

section[data-testid="stMain"]:has(.collage-page-marker) button[kind="secondary"] {{
  min-height: 38px;
  background: #242424 !important;
  color: #d8d8d8 !important;
  border: 0 !important;
  border-radius: 7px !important;
  font-size: 12px !important;
  font-weight: 500 !important;
}}

section[data-testid="stMain"]:has(.collage-page-marker) button[kind="secondary"] p {{
  color: inherit !important;
  font-size: 12px !important;
  font-weight: 500 !important;
}}

section[data-testid="stMain"]:has(.collage-page-marker) button[kind="primary"] {{
  min-height: 42px;
  background: #fff !important;
  color: #050505 !important;
  border: 0 !important;
  border-radius: 7px !important;
  font-size: 13px !important;
  font-weight: 800 !important;
}}

section[data-testid="stMain"]:has(.collage-page-marker) button[kind="primary"] p {{
  color: inherit !important;
  font-size: 13px !important;
  font-weight: 800 !important;
}}

@media (max-width: 760px) {{
  .persona-guide-grid {{
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }}

  .persona-guide-card {{
    min-height: 126px;
  }}

  .main-title {{
    margin-top: 34px;
    margin-bottom: 40px;
  }}

  div[data-testid="stVerticalBlockBorderWrapper"]:has(.result-page-marker),
  div[data-testid="stVerticalBlockBorderWrapper"]:has(.price-page-marker) {{
    padding-left: 20px;
    padding-right: 20px;
  }}

  .collage-right-shell {{
    max-height: none;
    overflow: visible;
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
    "오피스룩": "단정한 테일러링과 절제된 컬러로 세련된 비즈니스 무드를 완성합니다.",
}

WOMEN_GUIDE_PERSONAS = [
    "클래식", "프레피룩", "미니멀", "오피스룩",
    "워크웨어", "레트로", "고프코어", "걸리시",
    "시크", "스트릿", "스포티", "캐주얼",
]

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
# 4. Lite 추천 로직 연결
# ============================================================

def get_price_ranges(gender=None):
    return get_lite_price_ranges(
        gender=gender,
        npz_path=MASTER_DATA_PATH,
        persona_item_path=PERSONA_ITEM_PATH,
        excluded_path=EXCLUDED_PRODUCT_PATH,
    )


def recommend_products(persona, budget=None, gender=None, top_n=5):
    return recommend_lite_products(
        persona=persona,
        budget=budget,
        gender=gender,
        top_n=top_n,
        npz_path=MASTER_DATA_PATH,
        persona_item_path=PERSONA_ITEM_PATH,
        excluded_path=EXCLUDED_PRODUCT_PATH,
    )


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


def centered_button(label, key, on_click=None, button_type="secondary"):
    c1, c2, c3 = st.columns([1, 2.2, 1])
    with c2:
        clicked = st.button(
            label,
            key=key,
            use_container_width=True,
            type=button_type,
        )
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


def parse_price_value(value, fallback=0):
    cleaned = str(value).replace(",", "").replace("원", "").strip()
    if not cleaned:
        return int(fallback)
    try:
        return max(0, int(cleaned))
    except (TypeError, ValueError):
        return int(fallback)


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


def get_product_image_src(item):
    """
    사전 누끼 이미지가 있으면 우선 사용하고, 없으면 원본 img_url로 대체합니다.

    지원 경로:
      data/lite/processed_imgs/{product_id}.webp
      data/lite/processed_imgs/{product_id}.png
      data/lite/processed_imgs/{product_id}.jpg
    """
    if not item:
        return ""

    product_id = item.get("product_id")
    if product_id is not None:
        try:
            product_id = int(product_id)
            for suffix in (".webp", ".png", ".jpg", ".jpeg"):
                processed_path = PROCESSED_IMAGE_DIR / f"{product_id}{suffix}"
                if processed_path.exists():
                    return local_image_src(processed_path) or ""
        except (TypeError, ValueError):
            pass

    return item_img_src(item.get("img_url", ""))


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
    st.markdown("<div class='main-page-marker'></div>", unsafe_allow_html=True)
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
        button_type="primary",
    )

    centered_button(
        "여성 스냅 페르소나 검사하기",
        "main_women_start",
        lambda: start_women_test(),
        button_type="primary",
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

    centered_button("이전 질문으로", f"{step}_{idx}_back", go_men_back, button_type="tertiary")


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

    with st.container(border=True):
        st.markdown("<div class='result-page-marker'></div>", unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class="result-card-copy fade-in">
              <p class="result-card-label">당신의 페르소나는</p>
              <h1 class="result-card-title">{html.escape(result)}</h1>
              <p class="result-card-desc">{html.escape(desc)}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col_confirm, col_retry = st.columns(2, gap="small")
        with col_confirm:
            if st.button("확인", key="men_result_confirm", use_container_width=True):
                go("price_setting")
        with col_retry:
            if st.button("다시하기", key="men_result_retry", use_container_width=True):
                reset_all()

        if st.button(
            "모든 페르소나 설명 보기",
            key="men_result_desc",
            use_container_width=True,
            type="tertiary",
        ):
            go("descriptions")


def render_descriptions():
    st.markdown("<div class='guide-page-marker'></div>", unsafe_allow_html=True)

    if st.session_state.gender == "women":
        names = WOMEN_GUIDE_PERSONAS
        descriptions = WOMEN_PERSONA_DESCRIPTIONS
    else:
        names = PERSONAS
        descriptions = PERSONA_DESCRIPTIONS

    cards = []
    for name in names:
        desc = descriptions.get(name, "")
        cards.append(
            f"""
            <article class="persona-guide-card">
              <div class="persona-guide-name">{html.escape(name)}</div>
              <p class="persona-guide-desc">{html.escape(desc)}</p>
            </article>
            """
        )

    st.markdown(
        f"""
        <section class="fade-in">
          <h2 class="guide-page-title">페르소나 가이드</h2>
          <div class="persona-guide-grid">
            {''.join(cards)}
          </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    centered_button(
        "결과로 돌아가기",
        "desc_back",
        lambda: go("women_result" if st.session_state.gender == "women" else "result"),
        button_type="tertiary",
    )

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

    persona = final["persona"]
    desc = final["description"]

    with st.container(border=True):
        st.markdown("<div class='result-page-marker'></div>", unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class="result-card-copy fade-in">
              <p class="result-card-label">당신의 페르소나는</p>
              <h1 class="result-card-title">{html.escape(persona)}</h1>
              <p class="result-card-desc">{html.escape(desc)}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col_confirm, col_retry = st.columns(2, gap="small")
        with col_confirm:
            if st.button("확인", key="women_result_confirm", use_container_width=True):
                go("price_setting")
        with col_retry:
            if st.button("다시하기", key="women_result_retry", use_container_width=True):
                start_women_test()

        if st.button(
            "모든 페르소나 설명 보기",
            key="women_result_desc",
            use_container_width=True,
            type="tertiary",
        ):
            go("descriptions")

def render_price_setting():
    persona = st.session_state.result
    if not persona:
        go("main")

    ranges = get_price_ranges(st.session_state.gender)

    category_labels = {
        "outer": "아우터",
        "top": "상의",
        "bottom": "하의",
        "shoes": "신발",
        "acc": "액세서리",
    }

    budget = {}
    has_error = False

    with st.container(border=True):
        st.markdown("<div class='price-page-marker'></div>", unsafe_allow_html=True)
        st.markdown(
            """
            <div class="price-card-head fade-in">
              <h2>예산 설정</h2>
              <p>각 카테고리별로 원하는 가격대를 입력해주세요.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        for cat, label in category_labels.items():
            r = ranges.get(cat, {"min": 0, "max": 300000})
            min_bound = int(r.get("min", 0))
            max_bound = int(r.get("max", 300000))
            if max_bound <= 0:
                max_bound = 300000

            with st.container(border=True):
                st.markdown("<div class='budget-row-marker'></div>", unsafe_allow_html=True)
                label_col, min_col, sep_col, max_col = st.columns(
                    [0.72, 1.48, 0.16, 1.48],
                    gap="small",
                )

                with label_col:
                    st.markdown(f"<div class='budget-label'>{html.escape(label)}</div>", unsafe_allow_html=True)
                with min_col:
                    min_text = st.text_input(
                        f"{label} 최소",
                        value=f"{min_bound:,}",
                        key=f"min_{cat}",
                        label_visibility="collapsed",
                    )
                with sep_col:
                    st.markdown("<div class='budget-separator'>~</div>", unsafe_allow_html=True)
                with max_col:
                    max_text = st.text_input(
                        f"{label} 최대",
                        value=f"{max_bound:,}",
                        key=f"max_{cat}",
                        label_visibility="collapsed",
                    )

            min_price = parse_price_value(min_text, min_bound)
            max_price = parse_price_value(max_text, max_bound)

            if min_price > max_price:
                has_error = True
                st.error(f"{label}: 최소 가격은 최대 가격보다 작아야 합니다.")

            budget[cat] = {"min": min_price, "max": max_price}

        st.session_state.budget = budget

        col_submit, col_reset = st.columns(2, gap="small")
        with col_submit:
            submit = st.button(
                "추천 상품 확인하기",
                key="price_submit",
                use_container_width=True,
                disabled=has_error,
            )
        with col_reset:
            retry = st.button("다시하기", key="price_reset", use_container_width=True)

        if submit:
            run_recommendation()
        if retry:
            reset_all()

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
    bg_src = get_background_src(persona) or ""

    category_order = ["outer", "top", "bottom", "shoes", "acc"]
    category_labels = {
        "outer": "OUTER",
        "top": "TOP",
        "bottom": "BOTTOM",
        "shoes": "SHOES",
        "acc": "ACC",
    }

    def make_component_item(item, cat):
        return {
            "product_id": item.get("product_id"),
            "product_name": str(item.get("product_name", "")),
            "price": int(item.get("price") or 0),
            "price_text": format_price(item.get("price")),
            "img_url": get_product_image_src(item),
            "category": cat,
            "category_label": category_labels.get(cat, cat.upper()),
        }

    def data_attr(item):
        return html.escape(json.dumps(item, ensure_ascii=False), quote=True)

    sections_html = []
    first_items_for_autoplace = {}

    for cat in category_order:
        raw_items = items_by_category.get(cat, [])[:5]
        component_items = [make_component_item(item, cat) for item in raw_items]
        if component_items:
            first_items_for_autoplace[cat] = component_items[0]

        cards_html = []
        for item in component_items:
            img_src = html.escape(item.get("img_url", ""), quote=True)
            name = html.escape(item.get("product_name", ""), quote=True)
            price = html.escape(item.get("price_text", "-"))
            payload = data_attr(item)
            cards_html.append(
                f'''
                <article class="item-card">
                  <div class="img-box">
                    <img class="draggable-product" src="{img_src}" alt="{name}" draggable="true" data-item="{payload}">
                  </div>
                  <p class="price-text">{price}</p>
                </article>
                '''
            )

        for _ in range(max(0, 5 - len(component_items))):
            cards_html.append(
                '''
                <article class="item-card empty-slot">
                  해당 상품 없음
                </article>
                '''
            )

        sections_html.append(
            f'''
            <section class="cat-section" data-cat="{html.escape(cat)}">
              <div class="cat-header">
                <span class="cat-name">{html.escape(category_labels.get(cat, cat.upper()))}</span>
                <button class="shuffle-btn" type="button" data-shuffle="{html.escape(cat)}">셔플</button>
              </div>
              <div class="item-grid">
                {''.join(cards_html)}
              </div>
            </section>
            '''
        )

    auto_payload_json = json.dumps(first_items_for_autoplace, ensure_ascii=False).replace("</", "<\\/")
    bg_style = f"background-image:url('{html.escape(bg_src, quote=True)}');" if bg_src else "background:#f4efe4;"

    component_html = f'''
<!doctype html>
<html>
<head>
<meta charset="utf-8" />
<style>
  * {{ box-sizing: border-box; }}
  html, body {{ margin: 0; padding: 0; width: 100%; height: 100%; overflow: hidden; background: #000; color: #fff; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }}
  .advanced-collage-layout {{ display: flex; flex-direction: row; width: 100%; height: 742px; background-color: #000; padding: 18px 34px 12px; gap: 62px; justify-content: center; align-items: center; overflow: hidden; }}
  .left-canvas-area {{ flex: 0 0 430px; height: 710px; display: flex; flex-direction: column; align-items: center; justify-content: center; }}
  .canvas-header {{ width: 100%; text-align: center; }}
  .instruction {{ font-size: 12px; color: #777; margin: 0 0 12px; letter-spacing: -0.01em; }}
  .collage-canvas {{ width: 390px; height: 542px; border: 1px solid #9ca3af; border-radius: 11px; position: relative; overflow: hidden; background-size: cover; background-position: center; box-shadow: none; }}
  .collage-canvas::after {{ content: ""; position: absolute; inset: 8px; border: 1px solid rgba(255,255,255,0.72); border-radius: 9px; pointer-events: none; z-index: 1; }}
  .canvas-item {{ position: absolute; cursor: move; z-index: 10; transform-origin: center center; }}
  .canvas-item img {{ width: 150px; user-select: none; pointer-events: none; filter: drop-shadow(0 5px 8px rgba(0,0,0,0.20)); }}
  .right-list-area {{ flex: 0 0 610px; height: 690px; display: flex; flex-direction: column; text-align: left; overflow-y: auto; padding-right: 12px; }}
  .right-list-area::-webkit-scrollbar {{ width: 5px; }} .right-list-area::-webkit-scrollbar-thumb {{ background: #333; border-radius: 999px; }}
  .sidebar-title {{ font-size: 17px; font-weight: 800; color: #fff; margin: 0 0 16px; letter-spacing: 1.5px; text-align: left; }}
  .cat-section {{ margin-bottom: 16px; }}
  .cat-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }}
  .cat-name {{ font-size: 12px; font-weight: 800; color: #fff; }}
  .shuffle-btn {{ min-width: 48px; height: 22px; padding: 0 10px; color: #bdbdbd; background: #262626; border: 1px solid #353535; border-radius: 5px; font-size: 10px; cursor: pointer; }}
  .item-grid {{ display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 10px; }}
  .item-card {{ min-width: 0; height: 104px; display: flex; flex-direction: column; align-items: center; justify-content: space-between; padding: 8px 5px 9px; overflow: hidden; background: #fff; border-radius: 9px; }}
  .item-card.empty-slot {{ justify-content: center; color: #8b8b8b; font-size: 10px; }}
  .img-box {{ width: 100%; height: 72px; display: flex; align-items: center; justify-content: center; }}
  .img-box img {{ width: 82%; height: 72px; object-fit: contain; cursor: grab; user-select: none; }}
  .price-text {{ margin: 0; color: #050505; font-size: 10px; line-height: 1; font-weight: 500; user-select: none; }}
  .action-button-group {{ display: flex; flex-direction: column; width: 100%; gap: 9px; padding-top: 12px; }}
  .button-group {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; width: 100%; }}
  .btn-secondary, .buy-red-btn {{ height: 38px; border-radius: 7px; border: 0; cursor: pointer; font-size: 12px; font-weight: 600; }}
  .btn-secondary {{ background: #242424; color: #d8d8d8; }} .btn-secondary:hover {{ background: #111; color: #fff; }}
  .buy-red-btn {{ width: 100%; height: 42px; background: #fff; color: #050505; font-weight: 800; }} .buy-red-btn:hover {{ background: #e5e5e5; }}
  .notice {{ color: #777; font-size: 11px; text-align: center; margin-top: 2px; }}
  .js-error {{ display: none; margin: 8px 0 0; padding: 8px; background: rgba(255, 77, 79, 0.14); border: 1px solid rgba(255, 77, 79, 0.35); border-radius: 8px; color: #ffb4b4; font-size: 11px; text-align: left; word-break: break-all; }}
</style>
</head>
<body>
  <div class="advanced-collage-layout">
    <section class="left-canvas-area">
      <div class="canvas-header"><p class="instruction">드래그: 배치 / 캔버스 안 드래그: 이동 / 휠: 크기 조절 / 우클릭: 삭제</p></div>
      <div id="canvas" class="collage-canvas" style="{bg_style}"></div>
    </section>
    <section class="right-list-area">
      <h2 id="title" class="sidebar-title">{html.escape(persona)} 스타일 추천</h2>
      <div id="catalog">{''.join(sections_html)}</div>
      <div class="action-button-group">
        <div class="button-group">
          <button class="btn-secondary" id="localResetBtn" type="button">초기화</button>
          <button class="btn-secondary" id="autoPlaceBtn" type="button">자동배치</button>
          <button class="btn-secondary" id="clearNoticeBtn" type="button">안내</button>
        </div>
        <button class="buy-red-btn" id="purchaseBtn" type="button">선택 후 구매하기</button>
        <div class="notice" id="notice">Streamlit Lite 데모: 캔버스 조작은 이 화면 안에서 작동합니다.</div>
        <div class="js-error" id="jsError"></div>
      </div>
    </section>
  </div>
<script>
(function() {{
  const AUTO_ITEMS = {auto_payload_json};
  const canvas = document.getElementById('canvas');
  const notice = document.getElementById('notice');
  const jsError = document.getElementById('jsError');
  const state = {{ selectedItems: [], draggingId: null, offsetX: 0, offsetY: 0, maxZ: 10 }};
  function showError(error) {{ if (!jsError) return; jsError.style.display = 'block'; jsError.textContent = 'JS 오류: ' + (error && error.message ? error.message : String(error)); }}
  window.addEventListener('error', function(event) {{ showError(event.error || event.message); }});
  function parseItemFromElement(el) {{ const raw = el.getAttribute('data-item'); if (!raw) return null; return JSON.parse(raw); }}
  function addCanvasItem(item, x, y, scale) {{ const id = Date.now() + '-' + Math.random().toString(16).slice(2); state.maxZ += 1; state.selectedItems.push({{...item, instanceId: id, x: x, y: y, scale: scale || 0.8, zIndex: state.maxZ}}); renderCanvas(); }}
  function renderCanvas() {{ Array.from(canvas.querySelectorAll('.canvas-item')).forEach(function(node) {{ node.remove(); }}); state.selectedItems.forEach(function(item) {{ const node = document.createElement('div'); node.className = 'canvas-item'; node.dataset.id = item.instanceId; node.style.left = item.x + 'px'; node.style.top = item.y + 'px'; node.style.transform = 'scale(' + item.scale + ')'; node.style.zIndex = item.zIndex; const img = document.createElement('img'); img.src = item.img_url; img.alt = item.product_name || ''; img.draggable = false; node.appendChild(img); attachCanvasHandlers(node, item); canvas.appendChild(node); }}); }}
  function attachCanvasHandlers(node, item) {{ node.addEventListener('mousedown', function(event) {{ event.preventDefault(); event.stopPropagation(); const target = state.selectedItems.find(function(it) {{ return it.instanceId === item.instanceId; }}); if (!target) return; state.draggingId = item.instanceId; state.offsetX = event.clientX - target.x; state.offsetY = event.clientY - target.y; state.maxZ += 1; target.zIndex = state.maxZ; node.style.zIndex = target.zIndex; }}); node.addEventListener('wheel', function(event) {{ event.preventDefault(); event.stopPropagation(); const target = state.selectedItems.find(function(it) {{ return it.instanceId === item.instanceId; }}); if (!target) return; const delta = event.deltaY > 0 ? -0.1 : 0.1; target.scale = Math.min(Math.max(target.scale + delta, 0.2), 3); node.style.transform = 'scale(' + target.scale + ')'; }}, {{ passive: false }}); node.addEventListener('contextmenu', function(event) {{ event.preventDefault(); state.selectedItems = state.selectedItems.filter(function(it) {{ return it.instanceId !== item.instanceId; }}); renderCanvas(); }}); }}
  document.querySelectorAll('.draggable-product').forEach(function(img) {{ img.addEventListener('dragstart', function(event) {{ const item = parseItemFromElement(img); if (!item) return; const raw = JSON.stringify(item); event.dataTransfer.setData('application/json', raw); event.dataTransfer.setData('text/plain', raw); }}); }});
  canvas.addEventListener('dragover', function(event) {{ event.preventDefault(); }});
  canvas.addEventListener('drop', function(event) {{ event.preventDefault(); const raw = event.dataTransfer.getData('application/json') || event.dataTransfer.getData('text/plain'); if (!raw) return; try {{ const item = JSON.parse(raw); const rect = canvas.getBoundingClientRect(); addCanvasItem(item, event.clientX - rect.left - 60, event.clientY - rect.top - 60, 0.8); }} catch (error) {{ showError(error); }} }});
  document.addEventListener('mousemove', function(event) {{ if (!state.draggingId) return; const target = state.selectedItems.find(function(it) {{ return it.instanceId === state.draggingId; }}); if (!target) return; target.x = event.clientX - state.offsetX; target.y = event.clientY - state.offsetY; const node = canvas.querySelector('[data-id="' + state.draggingId + '"]'); if (node) {{ node.style.left = target.x + 'px'; node.style.top = target.y + 'px'; }} }});
  document.addEventListener('mouseup', function() {{ state.draggingId = null; }});
  function autoPlace() {{ state.selectedItems = []; const positions = [{{cat:'outer',x:30,y:105,scale:1.18}},{{cat:'top',x:205,y:88,scale:1.05}},{{cat:'bottom',x:215,y:268,scale:1.05}},{{cat:'shoes',x:62,y:398,scale:0.92}},{{cat:'acc',x:182,y:178,scale:0.72}}]; positions.forEach(function(pos) {{ const item = AUTO_ITEMS[pos.cat]; if (!item) return; state.maxZ += 1; state.selectedItems.push({{...item, instanceId: Date.now() + '-' + Math.random().toString(16).slice(2), x: pos.x, y: pos.y, scale: pos.scale, zIndex: state.maxZ}}); }}); renderCanvas(); }}
  function clearCanvas() {{ state.selectedItems = []; renderCanvas(); }}
  function shuffleCategory(cat) {{ const section = document.querySelector('.cat-section[data-cat="' + cat + '"]'); if (!section) return; const grid = section.querySelector('.item-grid'); const cards = Array.from(grid.children); const productCards = cards.filter(function(card) {{ return !card.classList.contains('empty-slot'); }}); for (let i = productCards.length - 1; i > 0; i -= 1) {{ const j = Math.floor(Math.random() * (i + 1)); const temp = productCards[i]; productCards[i] = productCards[j]; productCards[j] = temp; }} grid.innerHTML = ''; productCards.forEach(function(card) {{ grid.appendChild(card); }}); cards.filter(function(card) {{ return card.classList.contains('empty-slot'); }}).forEach(function(card) {{ grid.appendChild(card); }}); }}
  function purchaseDemo() {{ if (!state.selectedItems.length) {{ alert('캔버스에 상품을 먼저 드래그해 주세요.'); return; }} const total = state.selectedItems.reduce(function(sum, item) {{ return sum + Number(item.price || 0); }}, 0); const names = state.selectedItems.map(function(item) {{ return '- ' + (item.product_name || item.category_label || '상품'); }}).join('\\n'); alert('선택 상품 ' + state.selectedItems.length + '개\\n총액: ' + total.toLocaleString() + '원\\n\\n' + names); }}
  document.getElementById('localResetBtn').onclick = clearCanvas;
  document.getElementById('autoPlaceBtn').onclick = autoPlace;
  document.getElementById('clearNoticeBtn').onclick = function() {{ notice.textContent = '상품 이미지를 오른쪽에서 왼쪽 캔버스로 드래그하세요. 캔버스 안에서는 이동/휠 확대/우클릭 삭제가 가능합니다.'; }};
  document.getElementById('purchaseBtn').onclick = purchaseDemo;
  document.querySelectorAll('[data-shuffle]').forEach(function(btn) {{ btn.addEventListener('click', function() {{ shuffleCategory(btn.getAttribute('data-shuffle')); }}); }});
  autoPlace();
}})();
</script>
</body>
</html>
'''

    st.markdown("<div class='collage-page-marker'></div>", unsafe_allow_html=True)
    components.html(component_html, height=762, scrolling=False)

    ctrl_home, ctrl_reset, ctrl_back = st.columns(3, gap="small")
    with ctrl_home:
        home_clicked = st.button("메인으로", key="collage_home", use_container_width=True)
    with ctrl_reset:
        reset_clicked = st.button("다른 추천 보기", key="shuffle_all", use_container_width=True)
    with ctrl_back:
        back_clicked = st.button("이전으로", key="collage_back", use_container_width=True)

    if home_clicked:
        reset_all()
    if reset_clicked:
        run_recommendation()
    if back_clicked:
        go("price_setting")


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
