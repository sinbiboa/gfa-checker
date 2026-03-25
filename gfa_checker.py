import streamlit as st
import requests
import io
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import easyocr
import os

# --- 1. 페이지 설정 및 디자인 ---
st.set_page_config(page_title="GFA AI Studio PRO", layout="wide")

st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #111111; color: #FFFFFF !important; }
    [data-testid="stSidebar"] label p { color: #FFFFFF !important; font-size: 20px !important; font-weight: 800 !important; }
    [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p { color: #FFFFFF !important; font-size: 18px !important; font-weight: 600 !important; }
    [data-testid="stSidebar"] .stButton button {
        background-color: #333333; color: #FFFFFF !important; font-size: 18px !important;
        font-weight: bold !important; height: 50px; border-radius: 10px; border: 2px solid #444444; margin-bottom: 10px;
    }
    .main-title { background-color: #00C73C; padding: 20px; border-radius: 15px; color: white; text-align: center; margin-bottom: 30px; }
    </style>
    <div class="main-title">
        <h1>🎯 GFA 광고 마스터 PRO</h1>
        <p>AI 이미지 생성 및 규격 자동 검수/리사이징 도구</p>
    </div>
    """, unsafe_allow_html=True)

# --- 2. 규격 데이터 ---
AD_SPECS = {
    "스마트채널 (1250x370)": {"w": 1250, "h": 370},
    "네이버 메인 (1250x560)": {"w": 1250, "h": 560},
    "피드형 (1200x628)": {"w": 1200, "h": 628},
    "1:1 규격 (1200x1200)": {"w": 1200, "h": 1200},
    "배너형 (342x228)": {"w": 342, "h": 228}
}

# --- 3. 메뉴 상태 관리 ---
if 'menu' not in st.session_state:
    st.session_state.menu = "🔍 규격 검수"
if 'current_bg' not in st.session_state:
    st.session_state.current_bg = None

st.sidebar.markdown("<p style='color:white; font-size:22px; font-weight:bold;'>🛠️ 메뉴 선택</p>", unsafe_allow_html=True)
if st.sidebar.button("🔍 GFA 광고 규격 검수", use_container_width=True):
    st.session_state.menu = "🔍 규격 검수"
if st.sidebar.button("🎨 AI 이미지 생성/편집", use_container_width=True):
    st.session_state.menu = "🎨 이미지 제작"

st.sidebar.markdown("---")

# --- 4. 메인 로직 ---

# [메뉴 1: 규격 검수]
if st.session_state.menu == "🔍 규격 검수":
    st.header("🔍 GFA 광고 규격 및 비중 검수")
    selected_ad = st.sidebar.selectbox("검수할 광고 유형", list(AD_SPECS.keys()))
    spec = AD_SPECS[selected_ad]
    
    uploaded_file = st.file_uploader(f"[{selected_ad}] 이미지 업로드", type=['jpg', 'png', 'jpeg'])
    if uploaded_file:
        img = Image.open(uploaded_file)
        w, h = img.size
        col_v, col_r = st.columns([1.5, 1])
        with col_r:
            st.subheader("📝 검수 리포트")
            if w == spec['w'] and h == spec['h']:
                st.success(f"✅ 해상도 일치 ({w}x{h})")
            else:
                st.error(f"❌ 규격 불일치 (현재 {w}x{h} / 권장 {spec['w']}x{spec['h']})")
                if st.button("🔄 자동 리사이징 하기"):
                    resized = img.resize((spec['w'], spec['h']), Image.Resampling.LANCZOS)
                    buf = io.BytesIO()
                    resized.convert("RGB").save(buf, format="JPEG", quality=90)
                    st.download_button("📥 리사이징 이미지 다운로드", buf.getvalue(), f"fixed_{w}x{h}.jpg", "image/jpeg")
        with col_v:
            st.image(img, use_container_width=True)

# [메뉴 2: 이미지 제작] (복구 완료!)
elif st.session_state.menu == "🎨 이미지 제작":
    st.header("🎨 AI 이미지 생성 및 문구 자유 합성")
    
    st.sidebar.markdown("<p style='color:white; font-size:18px;'>📍 배경 설정</p>", unsafe_allow_html=True)
    selected_gen_ad = st.sidebar.selectbox("생성 규격 선택", list(AD_SPECS.keys()))
    gen_spec = AD_SPECS[selected_gen_ad]
    bg_source = st.sidebar.radio("배경 방법", ["AI로 생성하기", "내 이미지 업로드"])
    
    st.sidebar.markdown("<p style='color:white; font-size:18px;'>✍️ 텍스트 설정</p>", unsafe_allow_html=True)
    ad_text = st.sidebar.text_input("합성 문구", "GFA 마케팅의 시작!")
    text_color = st.sidebar.color_picker("글자 색상", "#FFFFFF")
    text_size = st.sidebar.slider("글자 크기", 20, 300, 100) # 🌟 크기 조절 슬라이더
    
    st.sidebar.markdown("<p style='color:white; font-size:16px;'>위치 조절</p>", unsafe_allow_html=True)
    pos_x = st.sidebar.slider("좌우 위치", 0, gen_spec['w'], int(gen_spec['w']/2))
    pos_y = st.sidebar.slider("상하 위치", 0, gen_spec['h'], int(gen_spec['h']/2))

    col_ctrl, col_view = st.columns([1, 1.5])
    
    with col_ctrl:
        if bg_source == "AI로 생성하기":
            prompt = st.text_area("배경 설명 (영문)", "modern abstract background, professional, clean")
            if st.button("✨ AI 배경 생성"):
                with st.spinner("이미지 생성 중..."):
                    url = f"https://image.pollinations.ai/prompt/{prompt}?width={gen_spec['w']}&height={gen_spec['h']}&nologo=true"
                    res = requests.get(url)
                    if res.status_code == 200:
                        st.session_state.current_bg = Image.open(io.BytesIO(res.content)).convert("RGB")
                        st.rerun()
        else:
            up_bg = st.file_uploader("이미지 업로드", type=['jpg', 'png'])
            if up_bg:
                st.session_state.current_bg = Image.open(up_bg).convert("RGB").resize((gen_spec['w'], gen_spec['h']))

    with col_view:
        if st.session_state.current_bg:
            canvas = st.session_state.current_bg.copy()
            draw = ImageDraw.Draw(canvas)
            # 윈도우 기본 폰트 경로 설정 (Arial)
            f_path = "C:\\Windows\\Fonts\\arial.ttf"
            try:
                font = ImageFont.truetype(f_path, text_size) if os.path.exists(f_path) else ImageFont.load_default()
            except: font = ImageFont.load_default()
            
            draw.text((pos_x, pos_y), ad_text, fill=text_color, font=font, anchor="mm")
            st.image(canvas, use_container_width=True)
            
            buf = io.BytesIO()
            canvas.save(buf, format="JPEG", quality=95)
            st.download_button("📥 최종 이미지 다운로드", buf.getvalue(), "gfa_ad.jpg", "image/jpeg")
        else:
            st.info("배경을 생성하거나 업로드하면 편집기가 나타납니다.")
