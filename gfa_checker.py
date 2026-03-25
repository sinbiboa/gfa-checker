import streamlit as st
import requests
import io
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import easyocr

# --- 1. 페이지 설정 및 가독성 극대화 디자인 ---
st.set_page_config(page_title="GFA AI Studio PRO", layout="wide")

st.markdown("""
    <style>
    /* 사이드바 배경 및 글자 가독성 (매우 진하고 크게) */
    [data-testid="stSidebar"] {
        background-color: #111111; /* 완전 깊은 블랙 */
    }
    
    /* 사이드바의 모든 라벨(제목) 스타일 */
    [data-testid="stSidebar"] label p {
        color: #FFFFFF !important;
        font-size: 20px !important; /* 글씨 크기 대폭 확대 */
        font-weight: 800 !important; /* 매우 진하게 */
        margin-bottom: 10px;
    }

    /* 라디오 버튼 및 선택 항목 텍스트 스타일 */
    [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
        color: #FFFFFF !important;
        font-size: 18px !important;
        font-weight: 600 !important;
    }

    /* 사이드바 버튼 스타일 (진하고 크게) */
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
        <p>AI 이미지 생성 및 규격/텍스트 자동 분석</p>
    </div>
    """, unsafe_allow_html=True)

# --- 2. 상태 관리 및 메뉴 구성 ---
if 'menu' not in st.session_state:
    st.session_state.menu = "🎨 이미지 생성"

# 사이드바 상단 메뉴 버튼
st.sidebar.markdown("<p style='color:white; font-size:22px; font-weight:bold;'>🛠️ 도구 선택</p>", unsafe_allow_html=True)
if st.sidebar.button("🎨 이미지 생성하기", use_container_width=True):
    st.session_state.menu = "🎨 이미지 생성"
if st.sidebar.button("🔍 GFA 규격 검수", use_container_width=True):
    st.session_state.menu = "🔍 규격 검수"

st.sidebar.markdown("---")

# 광고 규격 데이터
AD_SPECS = {
    "스마트채널 (1250x370)": {"w": 1250, "h": 370, "limit": 500},
    "네이버 메인 (1250x560)": {"w": 1250, "h": 560, "limit": 500},
    "피드형 (1200x628)": {"w": 1200, "h": 628, "limit": 500},
    "1:1 규격 (1200x1200)": {"w": 1200, "h": 1200, "limit": 500},
    "배너형 (342x228)": {"w": 342, "h": 228, "limit": 500}
}

# --- 3. 메인 기능 로직 ---

# 메뉴 1: 이미지 생성
if st.session_state.menu == "🎨 이미지 생성":
    st.header("🎨 AI 이미지 생성 및 편집")
    
    st.sidebar.markdown("<p style='color:white; font-size:18px;'>📍 배경 설정</p>", unsafe_allow_html=True)
    selected_ad = st.sidebar.selectbox("대상 규격", list(AD_SPECS.keys()))
    bg_source = st.sidebar.radio("배경 확보", ["AI로 생성하기", "이미지 업로드"])
    
    st.sidebar.markdown("<p style='color:white; font-size:18px;'>✍️ 텍스트 설정</p>", unsafe_allow_html=True)
    ad_text = st.sidebar.text_input("넣을 문구", "야, 너도 GFA 할 수 있어!")
    text_color = st.sidebar.color_picker("글자 색상", "#FFFFFF")
    text_size = st.sidebar.slider("글자 크기", 20, 250, 100)

    col_view, col_ctrl = st.columns([1.5, 1])

    with col_ctrl:
        if bg_source == "AI로 생성하기":
            prompt = st.text_area("이미지 설명 (영문)", "High quality abstract commercial background, professional lighting, vibrant colors")
            if st.button("✨ AI 배경 생성 시작"):
                with st.spinner("이미지를 그리는 중입니다..."):
                    w, h = AD_SPECS[selected_ad]["w"], AD_SPECS[selected_ad]["h"]
                    gen_url = f"https://image.pollinations.ai/prompt/{prompt}?width={w}&height={h}&nologo=true"
                    res = requests.get(gen_url)
                    if res.status_code == 200:
                        st.session_state.current_bg = Image.open(io.BytesIO(res.content))
        else:
            uploaded_bg = st.file_uploader("배경 파일 업로드", type=['jpg', 'png'])
            if uploaded_bg:
                st.session_state.current_bg = Image.open(uploaded_bg)

    with col_view:
        if 'current_bg' in st.session_state:
            # 텍스트 합성 로직
            final_img = st.session_state.current_bg.copy().convert("RGB")
            draw = ImageDraw.Draw(final_img)
            try:
                # 폰트가 없을 경우를 대비해 기본 폰트 사용
                font = ImageFont.load_default()
            except:
                font = ImageFont.load_default()
            
            w, h = final_img.size
            draw.text((w/2, h/2), ad_text, fill=text_color, font=font, anchor="mm")
            
            st.image(final_img, use_container_width=True, caption="제작 중인 광고 이미지")
            
            # 저장 버튼
            buf = io.BytesIO()
            final_img.save(buf, format="JPEG", quality=95)
            st.download_button("📥 이미지 다운로드", buf.getvalue(), file_name="gfa_studio.jpg")
        else:
            st.info("왼쪽에서 배경을 생성하거나 업로드하면 편집 화면이 나타납니다.")

# 메뉴 2: 규격 검수
else:
    st.header("🔍 GFA 광고 규격 및 비중 검수")
    
    @st.cache_resource
    def load_ocr():
        return easyocr.Reader(['ko', 'en'], gpu=False)
    
    reader = load_ocr()
    
    uploaded_check = st.file_uploader("검수할 이미지를 올려주세요", type=['jpg', 'png', 'jpeg'])
    
    if uploaded_check:
        img = Image.open(uploaded_check)
        w, h = img.size
        st.write(f"📊 현재 해상도: {w}x{h}")
        # (여기에 기존 검수 로직이 이어집니다)
        st.image(img, use_container_width=True)
        st.success("이미지 분석 준비 완료!")
