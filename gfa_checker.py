import streamlit as st
import io
from PIL import Image, ImageDraw, ImageFont
import os

# --- 1. 페이지 설정 및 디자인 ---
st.set_page_config(page_title="GFA 통합 마스터", layout="wide")

st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #111111; color: #FFFFFF !important; }
    [data-testid="stSidebar"] label p { color: #FFFFFF !important; font-size: 18px !important; font-weight: 800 !important; }
    [data-testid="stSidebar"] .stButton button {
        background-color: #333333; color: #FFFFFF !important; font-size: 16px !important;
        font-weight: bold !important; height: 45px; border-radius: 10px; border: 1px solid #444444; margin-bottom: 10px;
    }
    .main-title { background-color: #00C73C; padding: 20px; border-radius: 15px; color: white; text-align: center; margin-bottom: 30px; }
    </style>
    <div class="main-title">
        <h1>🎯 GFA 광고 마스터 PRO</h1>
        <p>규격 검수 및 실시간 문구 합성 편집기</p>
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
    st.session_state.menu = "🔍 규격 검수"

# --- 3. 사이드바 메뉴 버튼 ---
st.sidebar.markdown("<p style='color:white; font-size:20px; font-weight:bold;'>🛠️ 메뉴 선택</p>", unsafe_allow_html=True)
if st.sidebar.button("🔍 GFA 규격 검수", use_container_width=True):
    st.session_state.menu = "🔍 규격 검수"
if st.sidebar.button("🎨 문구 합성 편집", use_container_width=True):
    st.session_state.menu = "🎨 문구 합성"

st.sidebar.markdown("---")

# --- 4. 메인 기능 로직 ---

# [탭 1: GFA 규격 검수]
if st.session_state.menu == "🔍 규격 검수":
    st.header("🔍 GFA 광고 규격 검수")
    selected_ad = st.sidebar.selectbox("검수할 규격 선택", list(AD_SPECS.keys()))
    spec = AD_SPECS[selected_ad]
    
    uploaded_check = st.file_uploader(f"[{selected_ad}] 검수할 이미지 업로드", type=['jpg', 'png', 'jpeg'], key="check_file")
    
    if uploaded_check:
        img = Image.open(uploaded_check)
        w, h = img.size
        col1, col2 = st.columns([1.5, 1])
        with col2:
            st.subheader("📝 검수 결과")
            if w == spec['w'] and h == spec['h']:
                st.success(f"✅ 규격 일치! ({w}x{h})")
            else:
                st.error(f"❌ 규격 불일치 (현재: {w}x{h} / 권장: {spec['w']}x{spec['h']})")
                if st.button("🔄 이 규격으로 리사이징"):
                    resized = img.resize((spec['w'], spec['h']), Image.Resampling.LANCZOS)
                    buf = io.BytesIO()
                    resized.convert("RGB").save(buf, format="JPEG", quality=90)
                    st.download_button("📥 리사이징 이미지 다운로드", buf.getvalue(), "fixed_ad.jpg", "image/jpeg")
        with col1:
            st.image(img, use_container_width=True, caption=f"업로드 이미지 ({w}x{h})")

# [탭 2: 문구 합성 편집]
elif st.session_state.menu == "🎨 문구 합성":
    st.header("🎨 문구 합성 편집기")
    
    # 사이드바 설정값들
    selected_gen = st.sidebar.selectbox("제작 규격 선택", list(AD_SPECS.keys()))
    gen_spec = AD_SPECS[selected_gen]
    
    uploaded_bg = st.sidebar.file_uploader("배경 이미지 불러오기", type=['jpg', 'png', 'jpeg'], key="bg_file")
    
    ad_text = st.sidebar.text_input("합성할 문구 입력", "GFA 광고 문구")
    text_color = st.sidebar.color_picker("글씨 색상 선택", "#FFFFFF") # 🎨 색상 선택 추가
    text_size = st.sidebar.slider("글자 크기", 10, 2000, 200) # 한계치 2000으로 적정 조절
    
    if uploaded_bg:
        # 1. 배경 이미지 로드 및 리사이징
        bg_img = Image.open(uploaded_bg).convert("RGB")
        canvas = bg_img.resize((gen_spec['w'], gen_spec['h']), Image.Resampling.LANCZOS)
        draw = ImageDraw.Draw(canvas)
        
        # 2. 폰트 설정 (윈도우 기본 맑은 고딕 또는 Arial)
        font_paths = ["C:\\Windows\\Fonts\\malgun.ttf", "C:\\Windows\\Fonts\\arial.ttf"]
        font = None
        for path in font_paths:
            if os.path.exists(path):
                font = ImageFont.truetype(path, text_size)
                break
        if not font:
            font = ImageFont.load_default()
            
        # 3. 정중앙 합성
        draw.text((gen_spec['w']//2, gen_spec['h']//2), ad_text, fill=text_color, font=font, anchor="mm")
        
        # 🌟 4. 미리보기 즉시 출력 (이 부분이 핵심입니다)
        st.subheader("📷 실시간 미리보기")
        st.image(canvas, use_container_width=True, caption=f"현재 규격: {selected_gen}")
        
        # 5. 다운로드 버튼
        buf = io.BytesIO()
        canvas.save(buf, format="JPEG", quality=95)
        st.download_button("📥 완성된 이미지 다운로드", buf.getvalue(), "gfa_edit.jpg", "image/jpeg", use_container_width=True)
    else:
        st.info("왼쪽 사이드바에서 이미지를 업로드하면 실시간 미리보기가 나타납니다.")
