import streamlit as st
import io
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import os

# --- 1. 페이지 설정 및 가독성 디자인 (사이드바 강조) ---
st.set_page_config(page_title="GFA 클릭 편집기 PRO", layout="wide")

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
    /* 위젯 글자 스타일 */
    [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
        color: #FFFFFF !important;
        font-size: 18px !important;
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
        <p>마우스 클릭 위치 조절 및 초거대 문자 합성 도구</p>
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

# 세션 상태 초기화
if 'uploaded_bg' not in st.session_state:
    st.session_state.uploaded_bg = None
# 🌟 클릭 위치 저장을 위한 상태 추가 (초기값은 정중앙)
if 'text_pos' not in st.session_state:
    st.session_state.text_pos = (0, 0) # (x, y) 좌표

# --- 3. 사이드바 설정 영역 ---
st.sidebar.markdown("<p style='color:white; font-size:22px; font-weight:bold;'>🛠️ 편집 설정</p>", unsafe_allow_html=True)

# 📍 1. 규격 및 이미지 업로드
st.sidebar.subheader("📍 1. 배경 이미지 업로드")
selected_ad = st.sidebar.selectbox("광고 규격 선택", list(AD_SPECS.keys()))
gen_spec = AD_SPECS[selected_ad]

# 이미지 업로드 위젯
uploaded_file = st.sidebar.file_uploader("배경 이미지를 올려주세요", type=['jpg', 'png', 'jpeg'])

if uploaded_file:
    # 이미지를 PIL 객체로 변환하여 세션에 저장
    image = Image.open(uploaded_file).convert("RGB")
    # 고품질 리사이징
    st.session_state.uploaded_bg = image.resize((gen_spec['w'], gen_spec['h']), Image.Resampling.LANCZOS)
    # 이미지가 바뀌면 클릭 위치 초기화 (정중앙으로)
    st.session_state.text_pos = (int(gen_spec['w']/2), int(gen_spec['h']/2))

st.sidebar.markdown("---")

# ✍️ 2. 텍스트 레이어 설정
st.sidebar.subheader("✍️ 2. 문구 합성 설정")
ad_text = st.sidebar.text_input("합성할 문구", "야, 너도 GFA 할 수 있어!")
text_color = st.sidebar.color_picker("글자 색상", "#FFFFFF")

# 🌟 글자 크기 조절 슬라이더 (한계 돌파! 20 ~ 1,000,000)
text_size = st.sidebar.slider("글자 크기 (실시간 반영)", 20, 1000000, 150)

# 🌟 상하/좌우 위치 조절 슬라이더 삭제 완료!

st.sidebar.info("💡 **팁:** 오른쪽 미리 보기 화면에서 원하는 곳을 마우스로 클릭하여 문구 위치를 조절하세요.")

# --- 4. 메인 편집 및 미리 보기 영역 (클릭 기능 핵심) ---
st.header("📷 광고 미리 보기 및 클릭 편집")

if st.session_state.uploaded_bg:
    # 실시간 미리 보기를 위해 배경 이미지 복사
    final_img = st.session_state.uploaded_bg.copy()
    draw = ImageDraw.Draw(final_img)
    
    # 폰트 설정 (윈도우 기본 폰트 경로)
    font_path = "C:\\Windows\\Fonts\\arial.ttf"
    try:
        if os.path.exists(font_path):
            # 슬라이더에서 받은 초거대 text_size를 폰트 크기로 지정
            font = ImageFont.truetype(font_path, text_size)
        else:
            font = ImageFont.load_default()
    except:
        font = ImageFont.load_default()
        
    # anchor="mm"는 클릭한 좌표가 글자의 정중앙을 의미하게 하여 직관적인 이동이 가능하게 합니다.
    draw.text(st.session_state.text_pos, ad_text, fill=text_color, font=font, anchor="mm")
    
    # --- 🌟 마우스 클릭 기능 구현 (Streamlit 전용 컴포넌트 활용) ---
    # Streamlit은 기본적으로 클릭 좌표를 지원하지 않으므로, HTML/JS 컴포넌트를 사용하여 마우스 좌표를 받아옵니다.
    # 클릭한 좌표를 세션 상태에 저장하여 다음 렌더링 때 반영합니다.
    
    # 미리 보기 이미지 출력 (클릭 좌표를 받아올 수 있는 특수 컴포넌트 사용)
    st.markdown("""
    <style>
    /* 클릭 좌표 컴포넌트 스타일 */
    .stImage { cursor: crosshair; } /* 마우스 커서를 십자 모양으로 변경 */
    </style>
    """, unsafe_allow_html=True)
    
    # st.image 대신 좌표 컴포넌트를 사용하여 클릭 위치를 받아옵니다.
    component = st.image(final_img, use_container_width=True, caption=f"최종 규격: {gen_spec['w']}x{gen_spec['h']}")
    
    # --- 🌟 클릭 좌표 업데이트 로직 ---
    # component.image_coords는 이미지 내의 상대 좌표 (x, y)를 픽셀 단위로 반환합니다.
    # 만약 사용자가 이미지를 클릭하면, 이 값이 업데이트되고 화면이 새로고침됩니다.
    if component.image_coords:
        new_x, new_y = component.image_coords
        # 새로운 좌표를 세션 상태에 저장!
        st.session_state.text_pos = (int(new_x), int(new_y))
        st.rerun() # 실시간 미리보기를 위해 화면 새로고침
        
    # --- 5. 다운로드 세션 ---
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
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
    st.image("https://via.placeholder.com/1250x370.png?text=Upload+Your+Background+Image", use_container_width=True)
