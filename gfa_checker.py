import streamlit as st
import requests
import io
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# --- 1. 페이지 설정 및 디자인 개선 ---
st.set_page_config(page_title="GFA AI Studio PRO", layout="wide")

st.markdown("""
    <style>
    [data-testid="stSidebar"] {
        background-color: #171717;
        color: #FFFFFF !important;
    }
    [data-testid="stSidebar"] .stText, [data-testid="stSidebar"] label {
        color: #F0F0F0 !important;
        font-weight: 500;
    }
    .stButton button {
        background-color: #262626;
        color: white;
        border: 1px solid #404040;
    }
    .stButton button:focus {
        border-color: #00C73C;
        color: #00C73C;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. 사이드바 메뉴 및 상태 관리 ---
if 'menu' not in st.session_state:
    st.session_state.menu = "🎨 이미지 생성"

st.sidebar.title("🛠️ GFA 도구 모음")

col_m1, col_m2 = st.sidebar.columns(2)
with col_m1:
    if st.button("🎨 이미지 생성"): st.session_state.menu = "🎨 이미지 생성"
with col_m2:
    if st.button("🔍 규격 검수"): st.session_state.menu = "🔍 규격 검수"

st.sidebar.markdown("---")

# --- 3. 광고 규격 데이터 ---
AD_SPECS = {
    "스마트채널 (1250x370)": {"w": 1250, "h": 370},
    "네이버 메인 (1250x560)": {"w": 1250, "h": 560},
    "피드형 (1200x628)": {"w": 1200, "h": 628},
    "1:1 규격 (1200x1200)": {"w": 1200, "h": 1200}
}

# --- 4. 메인 기능 구현 ---

if st.session_state.menu == "🎨 이미지 생성":
    st.title("🎨 AI 광고 이미지 제작")
    
    # 에러가 났던 설명 부분을 주석(#) 처리하여 안전하게 수정했습니다.
    # 해상도 및 비율: (예: 1200x600, 800x800 등) 설정한 규격과 일치하는지 확인.

    st.sidebar.subheader("📍 1. 규격 및 배경")
    selected_ad = st.sidebar.selectbox("광고 규격", list(AD_SPECS.keys()))
    bg_source = st.sidebar.radio("배경 확보 방법", ["AI로 생성하기", "내 이미지 업로드"])
    
    st.sidebar.subheader("✍️ 2. 텍스트 레이어 설정")
    ad_text = st.sidebar.text_input("이미지에 넣을 문구", "여기에 문구를 입력하세요")
    text_color = st.sidebar.color_picker("글자 색상", "#FFFFFF")
    text_size = st.sidebar.slider("글자 크기", 20, 200, 80)
    
    col_view, col_ctrl = st.columns([1.5, 1])

    with col_ctrl:
        if bg_source == "AI로 생성하기":
            prompt = st.text_area("배경 프롬프트 (영문 권장)", "Beautiful abstract green nature background, high resolution, no text")
            if st.button("✨ 배경 생성"):
                with st.spinner("이미지 생성 중..."):
                    w, h = AD_SPECS[selected_ad]["w"], AD_SPECS[selected_ad]["h"]
                    gen_url = f"https://image.pollinations.ai/prompt/{prompt}?width={w}&height={h}&nologo=true"
                    res = requests.get(gen_url)
                    if res.status_code == 200:
                        st.session_state.current_bg = Image.open(io.BytesIO(res.content))
        else:
            uploaded_bg = st.file_uploader("배경 이미지를 선택하세요", type=['jpg', 'png'])
            if uploaded_bg:
                st.session_state.current_bg = Image.open(uploaded_bg)

    with col_view:
        if 'current_bg' in st.session_state:
            img_with_text = st.session_state.current_bg.copy()
            draw = ImageDraw.Draw(img_with_text)
            
            try:
                # 윈도우/맥 환경에 맞춰 폰트를 불러오거나 기본 폰트 사용
                font = ImageFont.load_default()
            except:
                font = ImageFont.load_default()
                
            w, h = img_with_text.size
            draw.text((w/2, h/2), ad_text, fill=text_color, font=font, anchor="mm")
            
            st.image(img_with_text, use_container_width=True)
            
            buf = io.BytesIO()
            img_with_text.save(buf, format="PNG")
            st.download_button("📥 완성된 이미지 저장", buf.getvalue(), file_name="gfa_ad.png")
        else:
            st.warning("먼저 배경 이미지를 생성하거나 업로드해주세요.")

else:
    st.title("🔍 GFA 광고 규격 검수")
    st.info("이미지 업로드 기능을 통해 규격과 텍스트 비중을 확인해 보세요.")
