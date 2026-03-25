import streamlit as st
import io
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import os

# --- 1. 페이지 설정 및 디자인 (가독성 극대화) ---
st.set_page_config(page_title="GFA 광고 편집기 PRO", layout="wide")

st.markdown("""
    <style>
    /* [개선] 사이드바 전체 가독성 강화 */
    [data-testid="stSidebar"] {
        background-color: #111111; /* 깊은 블랙 배경 */
        color: #FFFFFF !important;
    }
    
    /* [개선] 사이드바 제목/라벨 (크고 진하게) */
    [data-testid="stSidebar"] label p {
        color: #FFFFFF !important;
        font-size: 18px !important;
        font-weight: 800 !important;
        margin-bottom: 8px;
    }
    
    /* [수정] 라디오 버튼 텍스트 가독성 문제 해결 (image_0.png 반영) */
    [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
        color: #FFFFFF !important; /* 선택/미선택 모두 순백색 */
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
        <p>이미지 업로드 및 대형 문구 자유 합성 도구</p>
    </div>
    """, unsafe_allow_html=True)

# --- 2. 상태 관리 및 규격 데이터 ---
AD_SPECS = {
    "스마트채널 (1250x370)": {"w": 1250, "h": 370},
    "네이버 메인 (1250x560)": {"w": 1250, "h": 560},
    "피드형 (1200x628)": {"w": 1200, "h": 628},
    "1:1 규격 (1200x1200)": {"w": 1200, "h": 1200},
    "배너형 (342x228)": {"w": 342, "h": 228}
}

if 'uploaded_bg' not in st.session_state:
    st.session_state.uploaded_bg = None

# --- 3. 사이드바 설정 (이미지 업로드 및 텍스트) ---
st.sidebar.markdown("<p style='color:white; font-size:20px; font-weight:bold;'>🛠️ 편집 설정</p>", unsafe_allow_html=True)

# 규격 및 업로드
selected_ad = st.sidebar.selectbox("광고 규격 선택", list(AD_SPECS.keys()))
gen_spec = AD_SPECS[selected_ad]
uploaded_file = st.sidebar.file_uploader("배경 이미지를 올려주세요", type=['jpg', 'png', 'jpeg'])

if uploaded_file:
    # 이미지를 PIL 객체로 변환하여 세션에 저장
    image = Image.open(uploaded_file).convert("RGB")
    # 고품질 리사이징
    st.session_state.uploaded_bg = image.resize((gen_spec['w'], gen_spec['h']), Image.Resampling.LANCZOS)

st.sidebar.markdown("---")

# 텍스트 설정
# [수정] 기본 텍스트를 image_1.png에 맞춰 보라색으로
ad_text = st.sidebar.text_input("합성할 문구", "보라색 텍스트 입력")
text_color = st.sidebar.color_picker("글자 색상", "#8A2BE2") # BlueViolet

# [🌟핵심 수정] 글자 크기 한계 돌파! (20 ~ 800)
# image_1.png의 문제를 해결하기 위해 최대 범위를 800까지 늘렸습니다.
text_size = st.sidebar.slider("글자 크기 (초대형 가능)", 20, 800, 250)

# 위치 조절
text_pos_x = st.sidebar.slider("좌우 위치", 0, gen_spec['w'], int(gen_spec['w']/2))
text_pos_y = st.sidebar.slider("상하 위치", 0, gen_spec['h'], int(gen_spec['h']/2))

# --- 4. 메인 편집 및 미리 보기 영역 ---
st.header("📷 광고 미리 보기 및 편집")

if st.session_state.uploaded_bg:
    final_img = st.session_state.uploaded_bg.copy()
    draw = ImageDraw.Draw(final_img)
    
    # 윈도우 기본 폰트(Arial) 설정 - 크기 조절 가능
    font_path = "C:\\Windows\\Fonts\\arial.ttf" # 윈도우 기본 폰트 경로
    try:
        if os.path.exists(font_path):
            # [🌟반영] 슬라이더에서 받은 대형 text_size를 폰트에 적용
            font = ImageFont.truetype(font_path, text_size)
        else:
            font = ImageFont.load_default()
    except:
        font = ImageFont.load_default()
        
    # [🌟반영] 슬라이더로 조절한 크기와 위치(anchor="mm")에 텍스트 합성
    draw.text((text_pos_x, text_pos_y), ad_text, fill=text_color, font=font, anchor="mm")
    
    # 미리 보기 출력
    st.image(final_img, use_container_width=True, caption=f"최종 규격: {gen_spec['w']}x{gen_spec['h']}")
    
    # --- 5. 다운로드 ---
    st.markdown("---")
    buf = io.BytesIO()
    final_img.save(buf, format="JPEG", quality=95)
    st.download_button(
        label="📥 완성된 GFA 이미지 다운로드",
        data=buf.getvalue(),
        file_name=f"GFA_{selected_ad}.jpg",
        mime="image/jpeg",
        use_container_width=True
    )
else:
    st.info("왼쪽 사이드바에서 [배경 이미지]를 업로드하면 편집 화면이 나타납니다.")
    # 플레이스홀더
    st.image("https://via.placeholder.com/1250x370.png?text=Upload+Your+Background+Image", use_container_width=True)
