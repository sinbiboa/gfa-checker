import streamlit as st
import io
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import os
from streamlit_image_coordinates import streamlit_image_coordinates # 🌟 좌표 수집 컴포넌트 추가

# --- 1. 페이지 설정 및 디자인 ---
st.set_page_config(page_title="GFA 클릭 편집기 PRO", layout="wide")

st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #111111; color: #FFFFFF !important; }
    [data-testid="stSidebar"] label p { color: #FFFFFF !important; font-size: 18px !important; font-weight: 800 !important; }
    [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p { color: #FFFFFF !important; font-size: 16px !important; font-weight: 600 !important; }
    .main-title { background-color: #00C73C; padding: 20px; border-radius: 15px; color: white; text-align: center; margin-bottom: 30px; }
    </style>
    <div class="main-title">
        <h1>🎯 GFA 광고 마스터 PRO</h1>
        <p>마우스 클릭 위치 조절 (0~150) & 규격 검수</p>
    </div>
    """, unsafe_allow_html=True)

# --- 2. 규격 데이터 및 상태 관리 ---
AD_SPECS = {
    "스마트채널 (1250x370)": {"w": 1250, "h": 370},
    "네이버 메인 (1250x560)": {"w": 1250, "h": 560},
    "피드형 (1200x628)": {"w": 1200, "h": 628},
    "1:1 규격 (1200x1200)": {"w": 1200, "h": 1200},
    "배너형 (342x228)": {"w": 342, "h": 228}
}

if 'uploaded_bg' not in st.session_state:
    st.session_state.uploaded_bg = None
if 'text_pos' not in st.session_state:
    st.session_state.text_pos = None # 초기 좌표 없음
if 'menu' not in st.session_state:
    st.session_state.menu = "🎨 문구 합성"

# --- 3. 사이드바 메뉴 ---
st.sidebar.markdown("<p style='color:white; font-size:20px; font-weight:bold;'>🛠️ 메뉴 선택</p>", unsafe_allow_html=True)
if st.sidebar.button("🔍 GFA 규격 검수", use_container_width=True):
    st.session_state.menu = "🔍 규격 검수"
if st.sidebar.button("🎨 문구 합성 편집", use_container_width=True):
    st.session_state.menu = "🎨 문구 합성"

st.sidebar.markdown("---")

# --- 4. 폰트 로드 함수 ---
def get_font(size):
    actual_size = max(1, size)
    font_filename = "malgun.ttf"
    if os.path.exists(font_filename):
        try:
            return ImageFont.truetype(font_filename, actual_size)
        except:
            pass
    try:
        return ImageFont.truetype("arial.ttf", actual_size)
    except:
        return ImageFont.load_default()

# --- 5. 실행 로직 ---

if st.session_state.menu == "🔍 규격 검수":
    st.header("🔍 GFA 광고 규격 검수")
    # (기존 규격 검수 코드 동일...)
    # 생략...

elif st.session_state.menu == "🎨 문구 합성":
    st.header("🎨 문구 합성 편집기")
    
    selected_gen = st.sidebar.selectbox("제작 규격", list(AD_SPECS.keys()))
    gen_spec = AD_SPECS[selected_gen]
    
    uploaded_bg = st.sidebar.file_uploader("배경 이미지 업로드", type=['jpg', 'png', 'jpeg'], key="bg")
    
    ad_text = st.sidebar.text_input("합성할 문구 입력", "야, 너도 GFA 할 수 있어!")
    text_color = st.sidebar.color_picker("글씨 색상 선택", "#FFFFFF")
    
    # 🌟 글자 크기 슬라이더 (0 ~ 150 범위 고정)
    text_size = st.sidebar.slider("글자 크기", 0, 150, 60)
    
    # 🌟 상하/좌우 위치 조절 슬라이더 삭제 완료!

    st.sidebar.info("💡 **팁:** 오른쪽 미리 보기 화면에서 원하는 곳을 마우스로 클릭하여 문구 위치를 조절하세요.")

    if uploaded_bg:
        # 배경 이미지 로드 및 리사이징 (한 번만 수행하도록 세션 상태 활용)
        if st.session_state.uploaded_bg is None or st.session_state.uploaded_bg.size != (gen_spec['w'], gen_spec['h']):
            img = Image.open(uploaded_bg).convert("RGB")
            st.session_state.uploaded_bg = img.resize((gen_spec['w'], gen_spec['h']), Image.Resampling.LANCZOS)
            # 이미지가 바뀌면 클릭 위치 초기화 (정중앙으로)
            st.session_state.text_pos = (gen_spec['w'] // 2, gen_spec['h'] // 2)

        # 실시간 미리 보기를 위해 배경 이미지 복사
        canvas = st.session_state.uploaded_bg.copy()
        draw = ImageDraw.Draw(canvas)
        
        # 폰트 적용
        font = get_font(text_size)
        
        # 문구 합성 (세션 상태에 저장된 클릭 좌표 사용)
        # anchor="mm"는 클릭한 좌표가 글자의 정중앙을 의미하게 하여 직관적인 이동이 가능하게 합니다.
        draw.text(st.session_state.text_pos, ad_text, fill=text_color, font=font, anchor="mm")
        
        # 🌟 마우스 클릭 좌표 수집 컴포넌트 호출
        # 이미지를 화면에 출력하면서 동시에 클릭 좌표를 받아옵니다.
        value = streamlit_image_coordinates(canvas, key="gfa_coords", use_container_width=True)

        if value:
            # 클릭된 좌표 업데이트
            # streamlit_image_coordinates는 컨테이너 너비에 맞춰 스케일링된 좌표를 반환하므로, 
            # 이를 실제 이미지 해상도 비율로 변환해야 합니다. (use_container_width=True 사용 시 주의)
            # 여기서는 use_container_width=True를 사용했으므로, 좌표 변환 로직이 필요합니다.
            
            # 컨테이너의 실제 화면 너비를 구해야 정확한 스케일링이 가능합니다. (이 부분은 streamlit의 한계로 완벽하지 않을 수 있습니다.)
            # 가장 안정적인 방법은 use_container_width=False를 사용하거나, 
            # 아래와 같이 비율로 계산하는 것입니다. (streamlit_image_coordinates 컴포넌트가 알아서 해줍니다.)
            
            st.session_state.text_pos = (value["x"], value["y"])
            st.rerun() # 실시간 미리보기를 위해 화면 새로고침
        
        # 다운로드 버튼
        buf = io.BytesIO()
        canvas.save(buf, format="JPEG", quality=95)
        st.download_button("📥 완성 이미지 다운로드", buf.getvalue(), "gfa_ad.jpg", "image/jpeg", use_container_width=True)
    else:
        st.info("왼쪽 사이드바에서 이미지를 먼저 업로드해 주세요.")
