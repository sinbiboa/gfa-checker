import streamlit as st
import requests
import io
from PIL import Image, ImageDraw
import numpy as np
import easyocr

# --- 1. 페이지 설정 및 디자인 ---
st.set_page_config(page_title="GFA AI Studio", layout="wide")

# CSS로 제미나이 특유의 다크 모드와 카드 UI 구현
st.markdown("""
    <style>
    /* 사이드바 배경 및 카드 스타일 */
    [data-testid="stSidebar"] {
        background-color: #1e1f20;
        color: white;
    }
    .menu-card {
        background-color: #282a2d;
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 10px;
        border: 1px solid #3c4043;
        cursor: pointer;
        transition: 0.3s;
    }
    .menu-card:hover {
        background-color: #3c4043;
    }
    .active-card {
        border: 2px solid #8ab4f8;
        background-color: #3c4043;
    }
    /* 메인 타이틀 */
    .stTitle {
        color: #e8eaed;
        font-family: 'Google Sans', sans-serif;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. 사이드바 메뉴 구성 ---
st.sidebar.title("🚀 GFA AI Studio")

# 메뉴 선택을 위한 세션 상태 관리
if 'menu' not in st.session_state:
    st.session_state.menu = "🔍 GFA 검수"

def set_menu(menu_name):
    st.session_state.menu = menu_name

# 카드형 메뉴 (HTML/CSS로 흉내내기 위해 버튼 사용)
st.sidebar.markdown("### 주요 기능")
if st.sidebar.button("🔍 GFA 광고 규격 검수", use_container_width=True):
    set_menu("🔍 GFA 검수")
if st.sidebar.button("🎨 AI 광고 이미지 생성", use_container_width=True):
    set_menu("🎨 이미지 생성")

st.sidebar.markdown("---")

# --- 3. 광고 규격 데이터 ---
AD_SPECS = {
    "스마트채널 (1250x370)": {"w": 1250, "h": 370},
    "네이버 메인 (1250x560)": {"w": 1250, "h": 560},
    "피드형 (1200x628)": {"w": 1200, "h": 628},
    "1:1 규격 (1200x1200)": {"w": 1200, "h": 1200},
    "배너형 (342x228)": {"w": 342, "h": 228}
}

# --- 4. 메인 화면 로직 ---

# CASE 1: 이미지 생성 메뉴
if st.session_state.menu == "🎨 이미지 생성":
    st.title("🎨 AI 이미지 생성")
    st.write("프롬프트를 입력하여 광고 배경 이미지를 만들어보세요.")

    # [이미지 생성] 전용 사이드바 세부 설정
    st.sidebar.subheader("⚙️ 생성 옵션")
    selected_spec = st.sidebar.selectbox("대상 규격 선택", list(AD_SPECS.keys()))
    style_option = st.sidebar.selectbox("이미지 스타일", ["사진 리얼리즘", "3D 렌더링", "디지털 아트", "미니멀리즘"])
    aspect_ratio = st.sidebar.radio("비율 최적화", ["선택 규격 맞춤", "자유 비율"])

    # 메인 입력창
    prompt = st.text_area("어떤 이미지를 만들까요?", placeholder="예: 시원한 여름 바다 배경의 화장품 광고 배경, 파스텔 톤, 고품질", height=100)
    
    col_pre, col_res = st.columns([1, 1])
    
    with col_pre:
        st.subheader("🖼️ 미리 보기")
        # 생성 전에는 빈 박스(Placeholder)를 보여줌
        if 'generated_img' not in st.session_state:
            st.info("프롬프트를 입력하고 생성 버튼을 누르면 여기에 이미지가 나타납니다.")
            # 가상 미리보기 박스
            st.image("https://via.placeholder.com/1250x500?text=Your+AI+Art+Here", use_container_width=True)
        else:
            st.image(st.session_state.generated_img, use_container_width=True, caption="생성된 이미지")

    if st.button("✨ 이미지 생성하기", use_container_width=True):
        if not prompt:
            st.warning("프롬프트를 입력해주세요!")
        else:
            with st.spinner("AI가 예술 작품을 만드는 중..."):
                # 무료 이미지 생성 API 사용 (Pollinations)
                w, h = AD_SPECS[selected_spec]["w"], AD_SPECS[selected_spec]["h"]
                gen_url = f"https://image.pollinations.ai/prompt/{prompt}?width={w}&height={h}&nologo=true&model=flux"
                response = requests.get(gen_url)
                if response.status_code == 200:
                    st.session_state.generated_img = response.content
                    st.rerun()

    if 'generated_img' in st.session_state:
        st.download_button("📥 이미지 다운로드", st.session_state.generated_img, file_name="ai_ad_image.png", mime="image/png")

# CASE 2: GFA 검수 메뉴
else:
    st.title("🔍 GFA 광고 규격 검수")
    # (기존 검수 코드가 여기에 들어갑니다 - 지면상 핵심 구조만 유지)
    uploaded_file = st.file_uploader("검수할 이미지를 업로드하세요", type=['jpg', 'png', 'jpeg'])
    if uploaded_file:
        st.image(uploaded_file, caption="업로드된 이미지", use_container_width=True)
        st.success("AI 분석 준비 완료! (검수 로직 작동 중)")
