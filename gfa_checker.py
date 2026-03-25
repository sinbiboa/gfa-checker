import streamlit as st
import io
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import os
from streamlit_image_coordinates import streamlit_image_coordinates

# --- 1. 페이지 설정 및 디자인 ---
st.set_page_config(page_title="GFA 통합 마스터 PRO", layout="wide")

st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #111111; color: #FFFFFF !important; }
    [data-testid="stSidebar"] label p { color: #FFFFFF !important; font-size: 18px !important; font-weight: 800 !important; }
    .main-title { background-color: #00C73C; padding: 20px; border-radius: 15px; color: white; text-align: center; margin-bottom: 30px; }
    </style>
    <div class="main-title">
        <h1>🎯 GFA 광고 마스터 PRO</h1>
        <p>규격 검수 & 마우스 클릭 위치 조절 (0~150)</p>
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

if 'menu' not in st.session_state:
    st.session_state.menu = "🎨 문구 합성"
if 'text_pos' not in st.session_state:
    st.session_state.text_pos = (625, 185) # 초기 좌표 (스마트채널 중앙 기준)

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
    font_filename = "malgun.ttf" # GitHub에 올리신 파일명과 일치해야 함
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

# [탭 1: GFA 규격 검수]
if st.session_state.menu == "🔍 규격 검수":
    st.header("🔍 GFA 광고 규격 검수")
    selected_ad = st.sidebar.selectbox("검수 규격 선택", list(AD_SPECS.keys()))
    spec = AD_SPECS[selected_ad]
    uploaded_check = st.file_uploader(f"[{selected_ad}] 이미지 업로드", type=['jpg', 'png', 'jpeg'], key="check_file")
    
    if uploaded_check:
        img = Image.open(uploaded_check)
        w, h = img.size
        col1, col2 = st.columns([1.5, 1])
        with col2:
            st.subheader("📝 검수 결과")
            if w == spec['w'] and h == spec['h']:
                st.success(f"✅ 규격 일치! ({w}x{h})")
            else:
                st.error(f"❌ 불일치 (현재: {w}x{h} / 권장: {spec['w']}x{spec['h']})")
                if st.button("🔄 규격에 맞춰 리사이징"):
                    resized = img.resize((spec['w'], spec['h']), Image.Resampling.LANCZOS)
                    buf = io.BytesIO()
                    resized.convert("RGB").save(buf, format="JPEG", quality=95)
                    st.download_button("📥 리사이징 이미지 다운로드", buf.getvalue(), "fixed_gfa.jpg", "image/jpeg")
        with col1:
            st.image(img, use_container_width=True, caption=f"업로드 이미지 ({w}x{h})")

# [탭 2: 문구 합성 편집]
elif st.session_state.menu == "🎨 문구 합성":
    st.header("🎨 문구 합성 편집기")
    
    selected_gen = st.sidebar.selectbox("제작 규격 선택", list(AD_SPECS.keys()))
    gen_spec = AD_SPECS[selected_gen]
    
    uploaded_bg = st.sidebar.file_uploader("배경 이미지 불러오기", type=['jpg', 'png', 'jpeg'], key="bg_file")
    
    ad_text = st.sidebar.text_input("합성할 문구 입력", "야, 너도 GFA 할 수 있어!")
    text_color = st.sidebar.color_picker("글씨 색상 선택", "#FFFFFF")
    text_size = st.sidebar.slider("글자 크기 조절", 0, 150, 60) # 0 ~ 150 범위
    
    st.sidebar.info("💡 이미지 위를 클릭하면 문구가 해당 위치로 이동합니다.")

    if uploaded_bg:
        # 배경 이미지 로드 및 리사이징
        bg_img = Image.open(uploaded_bg).convert("RGB")
        canvas = bg_img.resize((gen_spec['w'], gen_spec['h']), Image.Resampling.LANCZOS)
        draw = ImageDraw.Draw(canvas)
        
        # 폰트 적용
        font = get_font(text_size)
        
        # 문구 합성 (세션 상태에 저장된 클릭 좌표 사용)
        draw.text(st.session_state.text_pos, ad_text, fill=text_color, font=font, anchor="mm")
        
        # 🌟 [에러 해결] PIL 이미지를 Numpy 배열로 변환하여 컴포넌트에 전달
        img_array = np.array(canvas)
        
        # 마우스 클릭 좌표 수집
        value = streamlit_image_coordinates(img_array, key="gfa_editor", use_container_width=True)

        if value:
            # 클릭된 좌표 업데이트 및 화면 갱신
            st.session_state.text_pos = (value["x"], value["y"])
            st.rerun()
        
        # 다운로드 버튼
        buf = io.BytesIO()
        canvas.save(buf, format="JPEG", quality=95)
        st.download_button("📥 완성된 이미지 다운로드", buf.getvalue(), "gfa_edit.jpg", "image/jpeg", use_container_width=True)
    else:
        st.info("왼쪽 사이드바에서 이미지를 업로드해 주세요.")
