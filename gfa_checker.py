import streamlit as st
import io
from PIL import Image, ImageDraw, ImageFont
import os
from streamlit_image_coordinates import streamlit_image_coordinates

# --- 1. 페이지 설정 및 디자인 ---
st.set_page_config(page_title="GFA 통합 편집기 PRO", layout="wide")

st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #111111; color: #FFFFFF !important; }
    [data-testid="stSidebar"] label p { color: #FFFFFF !important; font-size: 18px !important; font-weight: 800 !important; }
    [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p { color: #FFFFFF !important; font-size: 16px !important; font-weight: 600 !important; }
    .main-title { background-color: #00C73C; padding: 20px; border-radius: 15px; color: white; text-align: center; margin-bottom: 30px; }
    </style>
    <div class="main-title">
        <h1>🎯 GFA 광고 마스터 PRO</h1>
        <p>5대 필수 규격 지원 & 마우스 클릭 위치 조절</p>
    </div>
    """, unsafe_allow_html=True)

# --- 2. GFA 5대 규격 데이터 정의 ---
AD_SPECS = {
    "스마트채널 (1250x370)": {"w": 1250, "h": 370},
    "네이버 메인 (1250x560)": {"w": 1250, "h": 560},
    "피드형 (1200x628)": {"w": 1200, "h": 628},
    "1:1 규격 (1200x1200)": {"w": 1200, "h": 1200},
    "배너형 (342x228)": {"w": 342, "h": 228}
}

# 세션 상태 초기화
if 'uploaded_bg' not in st.session_state:
    st.session_state.uploaded_bg = None
if 'text_pos' not in st.session_state:
    st.session_state.text_pos = (625, 185) # 기본 중앙 좌표

# --- 3. 사이드바 설정 ---
st.sidebar.subheader("📍 1. 규격 및 이미지")
selected_ad = st.sidebar.selectbox("GFA 광고 규격 선택", list(AD_SPECS.keys()))
spec = AD_SPECS[selected_ad]

uploaded_file = st.sidebar.file_uploader("배경 이미지 업로드", type=['jpg', 'png', 'jpeg'])

if uploaded_file:
    img = Image.open(uploaded_file).convert("RGB")
    st.session_state.uploaded_bg = img.resize((spec['w'], spec['h']), Image.Resampling.LANCZOS)

st.sidebar.markdown("---")
st.sidebar.subheader("✍️ 2. 문구 설정")
ad_text = st.sidebar.text_input("합성할 문구", "보라색 텍스트 입력")
text_color = st.sidebar.color_picker("글자 색상", "#8A2BE2")

# 🌟 글자 크기 한계 돌파 (1,000,000)
text_size = st.sidebar.slider("글자 크기", 10, 1000000, 200)

# --- 4. 메인 편집 영역 ---
if st.session_state.uploaded_bg:
    final_img = st.session_state.uploaded_bg.copy()
    draw = ImageDraw.Draw(final_img)
    
    # 폰트 로드
    font_path = "C:\\Windows\\Fonts\\malgun.ttf" # 한글 폰트 경로 (윈도우 기준)
    try:
        font = ImageFont.truetype(font_path, text_size) if os.path.exists(font_path) else ImageFont.load_default()
    except:
        font = ImageFont.load_default()

    # 텍스트 그리기
    draw.text(st.session_state.text_pos, ad_text, fill=text_color, font=font, anchor="mm")
    
    st.info("💡 이미지 위를 클릭하면 문구가 해당 위치로 이동합니다.")
    
    # 🌟 마우스 클릭 좌표 수집 컴포넌트
    coords = streamlit_image_coordinates(final_img, key="gfa_coords", use_container_width=True)

    if coords:
        # 클릭된 좌표를 실제 이미지 해상도에 맞게 스케일링하여 저장
        st.session_state.text_pos = (coords["x"], coords["y"])
        st.rerun()

    # 다운로드 버튼
    buf = io.BytesIO()
    final_img.save(buf, format="JPEG", quality=95)
    st.download_button("📥 이미지 다운로드", buf.getvalue(), "gfa_ad.jpg", "image/jpeg", use_container_width=True)
else:
    st.info("왼쪽에서 배경 이미지를 먼저 업로드해 주세요.")
