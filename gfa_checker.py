import streamlit as st
import io
from PIL import Image, ImageDraw, ImageFont
import os

# --- 1. 페이지 설정 및 디자인 ---
st.set_page_config(page_title="GFA 통합 마스터 PRO", layout="wide")

st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #111111; color: white !important; }
    [data-testid="stSidebar"] label p { color: white !important; font-size: 15px !important; font-weight: bold; }
    .main-title { background-color: #00C73C; padding: 15px; border-radius: 10px; color: white; text-align: center; margin-bottom: 20px; }
    </style>
    <div class="main-title"><h1>🎯 GFA 광고 마스터 PRO</h1></div>
    """, unsafe_allow_html=True)

# --- 2. 폰트 로드 함수 ---
def get_font(size):
    actual_size = max(1, size)
    # 1순위: GitHub에 업로드한 맑은고딕 사용
    if os.path.exists("malgun.ttf"):
        return ImageFont.truetype("malgun.ttf", actual_size)
    # 2순위: 시스템 폰트 시도
    if os.path.exists("C:/Windows/Fonts/malgun.ttf"):
        return ImageFont.truetype("C:/Windows/Fonts/malgun.ttf", actual_size)
    return ImageFont.load_default()

# --- 3. GFA 규격 데이터 ---
AD_SPECS = {
    "스마트채널 (1250x370)": {"w": 1250, "h": 370},
    "네이버 메인 (1250x560)": {"w": 1250, "h": 560},
    "피드형 (1200x628)": {"w": 1200, "h": 628},
    "1:1 규격 (1200x1200)": {"w": 1200, "h": 1200},
    "배너형 (342x228)": {"w": 342, "h": 228}
}

# --- 4. 사이드바 설정 ---
st.sidebar.header("📂 1. 이미지 및 규격")
selected_ad = st.sidebar.selectbox("GFA 규격 선택", list(AD_SPECS.keys()))
spec = AD_SPECS[selected_ad]

uploaded_file = st.sidebar.file_uploader("배경 이미지 업로드", type=['jpg', 'png', 'jpeg'], key="main_upload")

st.sidebar.markdown("---")
st.sidebar.header("✍️ 2. 텍스트 설정 (최대 3개)")

# 텍스트 1 설정
with st.sidebar.expander("📝 텍스트 1 (Main)", expanded=True):
    txt1 = st.text_input("내용 1", "첫 번째 문구")
    clr1 = st.color_picker("색상 1", "#FFFFFF", key="c1")
    siz1 = st.slider("크기 1", 0, 150, 60, key="s1") # 🚀 0~150 제한
    x1 = st.slider("가로 위치 1", 0, spec['w'], spec['w']//2, key="x1")
    y1 = st.slider("세로 위치 1", 0, spec['h'], 100, key="y1")

# 텍스트 2 설정
with st.sidebar.expander("📝 텍스트 2 (Sub)"):
    txt2 = st.text_input("내용 2", "")
    clr2 = st.color_picker("색상 2", "#FFFFFF", key="c2")
    siz2 = st.slider("크기 2", 0, 150, 40, key="s2") # 🚀 0~150 제한
    x2 = st.slider("가로 위치 2", 0, spec['w'], spec['w']//2, key="x2")
    y2 = st.slider("세로 위치 2", 0, spec['h'], 200, key="y2")

# 텍스트 3 설정
with st.sidebar.expander("📝 텍스트 3 (Extra)"):
    txt3 = st.text_input("내용 3", "")
    clr3 = st.color_picker("색상 3", "#FFFFFF", key="c3")
    siz3 = st.slider("크기 3", 0, 150, 30, key="s3") # 🚀 0~150 제한
    x3 = st.slider("가로 위치 3", 0, spec['w'], spec['w']//2, key="x3")
    y3 = st.slider("세로 위치 3", 0, spec['h'], 300, key="y3")

# --- 5. 메인 로직 ---
if uploaded_file:
    try:
        # 이미지 로드 및 리사이징
        img = Image.open(uploaded_file).convert("RGB")
        canvas = img.resize((spec['w'], spec['h']), Image.Resampling.LANCZOS)
        draw = ImageDraw.Draw(canvas)

        # 텍스트 합성
        if txt3:
            draw.text((x3, y3), txt3, fill=clr3, font=get_font(siz3), anchor="mm")
        if txt2:
            draw.text((x2, y2), txt2, fill=clr2, font=get_font(siz2), anchor="mm")
        if txt1:
            draw.text((x1, y1), txt1, fill=clr1, font=get_font(siz1), anchor="mm")

        # 결과 출력
        st.subheader("📷 광고 미리보기")
        st.image(canvas, use_container_width=True)

        # 다운로드 버튼
        buf = io.BytesIO()
        canvas.save(buf, format="JPEG", quality=95)
        st.download_button(
            "📥 이미지 다운로드", 
            buf.getvalue(), 
            f"gfa_{selected_ad}.jpg", 
            "image/jpeg", 
            use_container_width=True
        )
    except Exception as e:
        st.error(f"이미지를 처리하는 중 오류가 발생했습니다: {e}")
else:
    st.info("왼쪽 사이드바에서 이미지를 업로드해 주세요.")
