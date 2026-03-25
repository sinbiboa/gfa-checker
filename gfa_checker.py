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
        <p>AI 이미지 생성 및 문구 자유 합성 도구 (Win)</p>
    </div>
    """, unsafe_allow_html=True)

# --- 2. 메뉴 및 규격 데이터 설정 ---
if 'menu' not in st.session_state:
    st.session_state.menu = "🎨 이미지 제작"

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

# [메뉴 1: 규격 검수] (기존 로직 유지)
if st.session_state.menu == "🔍 규격 검수":
    st.header("🔍 GFA 광고 규격 및 비중 검수")
    st.write("이미지를 올려 규격과 텍스트 비중을 확인하세요. (모든 규격 지원)")
    # (여기에 기존 검수 로직이 들어갑니다)

# [메뉴 2: 이미지 제작] (업그레이드 완료!)
elif st.session_state.menu == "🎨 이미지 제작":
    st.header("🎨 AI 이미지 생성 및 문구 합성")
    
    # --- 사이드바 설정 영역 ---
    st.sidebar.markdown("<p style='color:white; font-size:18px;'>📍 1. 배경 설정</p>", unsafe_allow_html=True)
    selected_gen_ad = st.sidebar.selectbox("생성할 광고 규격", list(AD_SPECS.keys()))
    gen_spec = AD_SPECS[selected_gen_ad]
    
    bg_source = st.sidebar.radio("배경 확보 방법", ["AI로 생성하기", "내 이미지 업로드"])
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("<p style='color:white; font-size:18px;'>✍️ 2. 텍스트 레이어 설정</p>", unsafe_allow_html=True)
    ad_text = st.sidebar.text_input("합성할 문구", "야, 너도 GFA 할 수 있어!")
    text_color = st.sidebar.color_picker("글자 색상", "#FFFFFF")
    
    # 🌟 글자 크기 조절 슬라이더 (반영 완료!)
    text_size = st.sidebar.slider("글자 크기 (실시간 반영)", 20, 300, 100)
    
    # 문구 위치 조절 슬라이더
    st.sidebar.markdown("<p style='color:white; font-size:16px;'>이동 (상하/좌우)</p>", unsafe_allow_html=True)
    text_pos_y = st.sidebar.slider("상하 위치", 0, gen_spec['h'], int(gen_spec['h']/2))
    text_pos_x = st.sidebar.slider("좌우 위치", 0, gen_spec['w'], int(gen_spec['w']/2))

    # --- 메인 편집 영역 ---
    col_ctrl, col_view = st.columns([1, 1.5])
    
    # 세션 상태에 편집 중인 이미지 저장 (실시간 반영용)
    if 'current_bg' not in st.session_state:
        st.session_state.current_bg = None

    with col_ctrl:
        if bg_source == "AI로 생성하기":
            prompt = st.text_area("이미지 배경 설명 (영문 권장)", "Beautiful abstract lighting background, high resolution, soft focus")
            if st.button("✨ AI 배경 생성 시작"):
                with st.spinner("이미지를 그리는 중입니다..."):
                    gen_url = f"https://image.pollinations.ai/prompt/{prompt}?width={gen_spec['w']}&height={gen_spec['h']}&nologo=true"
                    res = requests.get(gen_url)
                    if res.status_code == 200:
                        st.session_state.current_bg = Image.open(io.BytesIO(res.content)).convert("RGB")
                        st.rerun() # 실시간 미리보기를 위해 화면 새로고침
        else:
            uploaded_bg = st.file_uploader("배경 이미지를 선택하세요", type=['jpg', 'png'])
            if uploaded_bg:
                st.session_state.current_bg = Image.open(uploaded_bg).convert("RGB")
                # 리사이징 (업로드한 이미지를 GFA 규격으로 맞춤)
                st.session_state.current_bg = st.session_state.current_bg.resize((gen_spec['w'], gen_spec['h']), Image.Resampling.LANCZOS)

    with col_view:
        st.subheader("📷 광고 이미지 미리 보기")
        
        if st.session_state.current_bg:
            # 실시간 미리 보기를 위한 합성 로직
            final_img = st.session_state.current_bg.copy()
            draw = ImageDraw.Draw(final_img)
            
            # 폰트 설정 (윈도우 기본 폰트 사용 - 크기 조절 가능)
            # 시스템에 따라 경로가 다를 수 있으므로 예외 처리 추가
            font_path = "C:\\Windows\\Fonts\\arial.ttf" # 윈도우 기본 Arial 폰트
            if os.path.exists(font_path):
                try:
                    # 슬라이더에서 받은 text_size를 폰트 크기로 지정!
                    font = ImageFont.truetype(font_path, text_size)
                except:
                    st.error("폰트를 불러오는 중 오류가 발생했습니다.")
                    font = ImageFont.load_default()
            else:
                st.warning("윈도우 기본 폰트를 찾을 수 없습니다. 기본 폰트를 사용하므로 크기 조절이 안 될 수 있습니다.")
                font = ImageFont.load_default()
            
            # 슬라이더로 조절한 위치에 텍스트 합성
            draw.text((text_pos_x, text_pos_y), ad_text, fill=text_color, font=font, anchor="mm")
            
            # 미리 보기 이미지 출력
            st.image(final_img, use_container_width=True, caption=f"최종 규격: {gen_spec['w']}x{gen_spec['h']}")
            
            # 다운로드 버튼
            buf = io.BytesIO()
            final_img.save(buf, format="JPEG", quality=95)
            st.download_button("📥 완성된 이미지 다운로드", buf.getvalue(), file_name="gfa_studio.jpg")
        else:
            # 배경이 없을 때 가이드
            st.info("왼쪽에서 배경을 생성하거나 업로드하면 여기에 미리 보기가 나타납니다.")
            st.image("https://via.placeholder.com/1250x370.png?text=Background+Needed", use_container_width=True)
