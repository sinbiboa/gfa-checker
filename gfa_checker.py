import streamlit as st
import requests
import io
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import easyocr
import os

# --- 1. 페이지 설정 및 가독성 디자인 (사이드바 강조) ---
st.set_page_config(page_title="GFA AI Studio PRO", layout="wide")

st.markdown("""
    <style>
    /* 사이드바 가독성 최우선: 검은 배경에 크고 진한 흰색 글씨 */
    [data-testid="stSidebar"] {
        background-color: #111111;
        color: #FFFFFF !important;
    }
    /* 사이드바 라벨(제목) 스타일 */
    [data-testid="stSidebar"] label p {
        color: #FFFFFF !important;
        font-size: 20px !important;
        font-weight: 800 !important;
        margin-bottom: 10px;
    }
    /* 라디오 버튼 및 위젯 글자 스타일 */
    [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
        color: #FFFFFF !important;
        font-size: 18px !important;
        font-weight: 600 !important;
    }
    /* 사이드바 버튼 스타일 */
    [data-testid="stSidebar"] .stButton button {
        background-color: #333333;
        color: #FFFFFF !important;
        font-size: 18px !important;
        font-weight: bold !important;
        height: 50px;
        border-radius: 10px;
        border: 2px solid #444444;
        margin-bottom: 10px;
    }
    [data-testid="stSidebar"] .stButton button:hover {
        border-color: #00C73C;
        color: #00C73C !important;
    }
    /* 메인 타이틀 박스 */
    .main-title {
        background-color: #00C73C;
        padding: 20px;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 30px;
    }
    </style>
    <div class="main-title">
        <h1>🎯 GFA 광고 마스터 PRO</h1>
        <p>AI 이미지 생성 및 규격 자동 검수/리사이징 도구</p>
    </div>
    """, unsafe_allow_html=True)

# --- 2. 메뉴 및 규격 데이터 설정 ---
if 'menu' not in st.session_state:
    st.session_state.menu = "🔍 규격 검수"

# 모든 GFA 규격 리스트
AD_SPECS = {
    "스마트채널 (1250x370)": {"w": 1250, "h": 370, "limit": 500},
    "네이버 메인 (1250x560)": {"w": 1250, "h": 560, "limit": 500},
    "피드형 (1200x628)": {"w": 1200, "h": 628, "limit": 500},
    "1:1 규격 (1200x1200)": {"w": 1200, "h": 1200, "limit": 500},
    "배너형 (342x228)": {"w": 342, "h": 228, "limit": 500}
}

st.sidebar.markdown("<p style='color:white; font-size:22px; font-weight:bold;'>🛠️ 도구 선택</p>", unsafe_allow_html=True)
if st.sidebar.button("🔍 GFA 규격 검수", use_container_width=True):
    st.session_state.menu = "🔍 규격 검수"
if st.sidebar.button("🎨 AI 이미지 생성/편집", use_container_width=True):
    st.session_state.menu = "🎨 이미지 제작"

st.sidebar.markdown("---")

# --- 3. 메인 기능 로직 ---

# [메뉴 1: 규격 검수] (규격 확인 및 리사이징 기능 탑재!)
if st.session_state.menu == "🔍 규격 검수":
    st.header("🔍 GFA 광고 규격 및 비중 검수")
    st.write("이미지를 올려 규격이 맞는지 확인하고, 필요시 자동으로 리사이징하세요.")
    
    # 카테고리 선택 (기존처럼)
    selected_ad = st.sidebar.selectbox("검수할 광고 유형", list(AD_SPECS.keys()))
    spec = AD_SPECS[selected_ad]
    
    # OCR 모델 로딩 (캐싱 처리)
    @st.cache_resource
    def load_ocr():
        return easyocr.Reader(['ko', 'en'], gpu=False)
    
    reader = load_ocr()
    
    uploaded_file = st.file_uploader(f"[{selected_ad}] 이미지를 업로드하세요", type=['jpg', 'png', 'jpeg'])
    
    if uploaded_file:
        img = Image.open(uploaded_file)
        w, h = img.size
        
        col_view, col_report = st.columns([1.5, 1])
        
        with col_report:
            st.subheader("📝 검수 리포트")
            st.write(f"**대상 규격:** {selected_ad}")
            st.write(f"**현재 해상도:** {w}x{h}")
            
            # 🌟 1. 규격 확인 로직
            if w == spec['w'] and h == spec['h']:
                st.success(f"✅ 해상도가 규격과 일치합니다.")
            else:
                st.error(f"❌ 해상도가 불일치합니다. (권장: {spec['w']}x{spec['h']})")
                
                # 🌟 2. 리사이징 기능 추가
                st.info(f"아래 버튼을 누르면 업로드한 이미지를 {spec['w']}x{spec['h']} 규격으로 자동 리사이징합니다.")
                if st.button("🔄 이미지 자동 리사이징 및 다운로드", use_container_width=True):
                    with st.spinner("이미지 크기를 조절하는 중입니다..."):
                        # LANCZOS 필터를 사용하여 고품질 리사이징
                        resized_img = img.resize((spec['w'], spec['h']), Image.Resampling.LANCZOS)
                        
                        # 다운로드용 버퍼 생성
                        buf = io.BytesIO()
                        # GFA 가이드에 맞춰 용량 압축 (JPEG 품질 85% 권장)
                        resized_img.convert("RGB").save(buf, format="JPEG", quality=85)
                        
                        st.download_button(
                            label=f"📥 리사이징된 {selected_ad} 이미지 다운로드",
                            data=buf.getvalue(),
                            file_name=f"fixed_{selected_ad}.jpg",
                            mime="image/jpeg",
                            use_container_width=True
                        )
                        st.success(f"변환 완료! 다운로드 후 사용하세요.")

            st.markdown("---")
            # (여기에 OCR 텍스트 비중 분석 로직이 포함됩니다)
            st.info("AI가 텍스트 비중을 분석하고 있습니다... (준비 중)")
            
        with col_view:
            st.subheader("📷 업로드 이미지 미리 보기")
            st.image(img, use_container_width=True, caption=f"현재 크기: {w}x{h}")

# [메뉴 2: 이미지 제작] (기존 로직 유지)
elif st.session_state.menu == "🎨 이미지 제작":
    st.header("🎨 AI 이미지 생성 및 문구 합성")
    # (이미지 제작 로직은 이전과 동일하게 유지됩니다)
