import streamlit as st
import io
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import os

# --- 1. 페이지 설정 및 가독성 디자인 (사이드바 강조) ---
st.set_page_config(page_title="GFA 광고 편집기 PRO", layout="wide")

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
        font-size: 18px !important;
        font-weight: 800 !important;
        margin-bottom: 8px;
    }
    /* 위젯 글자 스타일 */
    [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
        color: #FFFFFF !important;
        font-size: 16px !important;
        font-weight: 600 !important;
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
        <p>이미지 업로드 및 대형 문구 합성 도구</p>
    </div>
    """, unsafe_allow_html=True)

# --- 2. 상태 관리 및 규격 데이터 설정 ---
# GFA 필수 규격 리스트
AD_SPECS = {
    "스마트채널 (1250x370)": {"w": 1250, "h": 370},
    "네이버 메인 (1250x560)": {"w": 1250, "h": 560},
    "피드형 (1200x628)": {"w": 1200, "h": 628},
    "1:1 규격 (1200x1200)": {"w": 1200, "h": 1200},
    "배너형 (342x228)": {"w": 342, "h": 228}
}

# 세션 상태 초기화 (업로드된 배경 이미지 저장)
if 'uploaded_bg' not in st.session_state:
    st.session_state.uploaded_bg = None

# --- 3. 사이드바 설정 영역 (요청하신 기능만 배치) ---
st.sidebar.markdown("<p style='color:white; font-size:20px; font-weight:bold;'>🛠️ 편집 설정</p>", unsafe_allow_html=True)

# 📍 1. 규격 및 이미지 불러오기 (image_uploader)
st.sidebar.subheader("📍 1. 이미지 불러오기")
selected_ad = st.sidebar.selectbox("GFA 광고 규격 선택", list(AD_SPECS.keys()))
gen_spec = AD_SPECS[selected_ad]

# 이미지 업로드 위젯
uploaded_file = st.sidebar.file_uploader("배경 이미지를 올려주세요", type=['jpg', 'png', 'jpeg'])

if uploaded_file:
    # 이미지를 PIL 객체로 변환하여 세션에 저장
    image = Image.open(uploaded_file).convert("RGB")
    # 선택한 GFA 규격으로 자동 리사이징 (고품질)
    st.session_state.uploaded_bg = image.resize((gen_spec['w'], gen_spec['h']), Image.Resampling.LANCZOS)

st.sidebar.markdown("---")

# ✍️ 2. 텍스트 입력 및 크기 (text_input / slider)
st.sidebar.subheader("✍️ 2. 문구 합성")
ad_text = st.sidebar.text_input("합성할 문구 입력", "야, 너도 GFA 할 수 있어!")
# text_color = st.sidebar.color_picker("글자 색상", "#FFFFFF") # 색상 선택 삭제

# 🌟 글자 크기 조절 슬라이더 (초대형 가능: 20 ~ 1,000,000)
text_size = st.sidebar.slider("글자 크기 (초대형 가능)", 20, 1000000, 200)

st.sidebar.info("💡 **팁:** 문구는 배경 이미지의 정중앙에 자동으로 위치합니다.")

# --- 4. 메인 편집 및 미리 보기 영역 ---
st.header("📷 광고 미리 보기 및 편집")

#업로드된 배경이 있을 때만 편집기 작동
if st.session_state.uploaded_bg:
    # 실시간 미리 보기를 위해 배경 이미지 복사
    final_img = st.session_state.uploaded_bg.copy()
    draw = ImageDraw.Draw(final_img)
    
    # 윈도우 기본 폰트(Arial) 설정 - 크기 조절 가능
    font_path = "C:\\Windows\\Fonts\\arial.ttf" # 윈도우 기본 폰트 경로
    try:
        if os.path.exists(font_path):
            # 슬라이더에서 받은 초거대 text_size를 폰트 크기로 지정
            font = ImageFont.truetype(font_path, text_size)
        else:
            font = ImageFont.load_default()
    except:
        font = ImageFont.load_default()
        
    # 문구를 배경 이미지의 정중앙(anchor="mm")에 합성
    # 색상은 흰색(#FFFFFF)으로 고정
    draw.text((gen_spec['w'] // 2, gen_spec['h'] // 2), ad_text, fill="#FFFFFF", font=font, anchor="mm")
    
    # 미리 보기 이미지 출력
    st.image(final_img, use_container_width=True, caption=f"최종 규격: {gen_spec['w']}x{gen_spec['h']}")
    
    # --- 5. 다운로드 세션 ---
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        # 다운로드용 버퍼 생성
        buf = io.BytesIO()
        # GFA 가이드에 맞춰 JPEG 품질 95%로 저장
        final_img.save(buf, format="JPEG", quality=95)
        
        st.download_button(
            label="📥 완성된 GFA 이미지 다운로드",
            data=buf.getvalue(),
            file_name=f"GFA_{selected_ad}.jpg",
            mime="image/jpeg",
            use_container_width=True
        )
else:
    # 배경이 없을 때 가이드 메시지
    st.info("왼쪽 사이드바에서 [배경 이미지]를 업로드하면 편집 화면이 나타납니다.")
    # 플레이스홀더 이미지
    st.image("https://via.placeholder.com/1250x370.png?text=Upload+Your+Background+Image", use_container_width=True)
