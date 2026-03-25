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
    [data-testid="stSidebar"] .stButton button:hover { border-color: #00C73C; color: #00C73C !important; }
    .main-title { background-color: #00C73C; padding: 20px; border-radius: 15px; color: white; text-align: center; margin-bottom: 30px; }
    </style>
    <div class="main-title">
        <h1>🎯 GFA 광고 마스터 PRO</h1>
        <p>규격 검수 및 심플 문구 합성 도구</p>
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

# --- 3. 사이드바 메뉴 버튼 (탭 복구) ---
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
    
    uploaded_check = st.file_uploader(f"[{selected_ad}] 검수할 이미지 업로드", type=['jpg', 'png', 'jpeg'], key="check")
    
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

# [탭 2: 문구 합성 편집] (요청하신 심플 버전)
elif st.session_state.menu == "🎨 문구 합성":
    st.header("🎨 심플 문구 합성")
    
    # 📍 1. 이미지 불러오기
    selected_gen = st.sidebar.selectbox("제작할 규격 선택", list(AD_SPECS.keys()))
    gen_spec = AD_SPECS[selected_gen]
    uploaded_bg = st.sidebar.file_uploader("배경 이미지 불러오기", type=['jpg', 'png', 'jpeg'], key="bg")
    
    # ✍️ 2. 텍스트 입력 및 크기
    ad_text = st.sidebar.text_input("합성할 문구 입력", "GFA 광고 문구")
    text_size = st.sidebar.slider("글자 크기 (한계 돌파)", 10, 1000000, 200)
    
    if uploaded_bg:
        # 배경 준비 및 자동 리사이징
        bg_img = Image.open(uploaded_bg).convert("RGB")
        canvas = bg_img.resize((gen_spec['w'], gen_spec['h']), Image.Resampling.LANCZOS)
        draw = ImageDraw.Draw(canvas)
        
        # 폰트 설정 (윈도우 기본)
        f_path = "C:\\Windows\\Fonts\\arial.ttf"
        try:
            font = ImageFont.truetype(f_path, text_size) if os.path.exists(f_path) else ImageFont.load_default()
        except:
            font = ImageFont.load_default()
            
        # 정중앙 합성 (흰색 고정)
        draw.text((gen_spec['w']//2, gen_spec['h']//2), ad_text, fill="#FFFFFF", font=font, anchor="mm")
        
        st.image(canvas, use_container_width=True, caption=f"편집 중: {selected_gen}")
        
        # 다운로드
        buf = io.BytesIO()
        canvas.save(buf, format="JPEG", quality=95)
        st.download_button("📥 완성된 이미지 다운로드", buf.getvalue(), "gfa_edit.jpg", "image/jpeg", use_container_width=True)
    else:
        st.info("왼쪽에서 이미지를 불러오면 편집기가 나타납니다.")
