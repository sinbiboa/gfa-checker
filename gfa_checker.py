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
    .main-title { background-color: #00C73C; padding: 20px; border-radius: 15px; color: white; text-align: center; margin-bottom: 30px; }
    </style>
    <div class="main-title">
        <h1>🎯 GFA 광고 마스터 PRO</h1>
        <p>폰트 파일 연동 완료! 글자 크기 및 규격 검수 통합본</p>
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

# --- 3. 사이드바 메뉴 ---
st.sidebar.markdown("<p style='color:white; font-size:20px; font-weight:bold;'>🛠️ 메뉴 선택</p>", unsafe_allow_html=True)
if st.sidebar.button("🔍 GFA 규격 검수", use_container_width=True):
    st.session_state.menu = "🔍 규격 검수"
if st.sidebar.button("🎨 문구 합성 편집", use_container_width=True):
    st.session_state.menu = "🎨 문구 합성"

st.sidebar.markdown("---")

# --- 4. 폰트 로드 함수 (핵심 수정!) ---
def get_font(size):
    # 🌟 1순위: GitHub에 직접 올린 malgun.ttf 파일 사용 (가장 확실함)
    font_filename = "malgun.ttf"
    
    if os.path.exists(font_filename):
        try:
            return ImageFont.truetype(font_filename, size)
        except:
            pass
            
    # 🌟 2순위: 윈도우 로컬 경로 시도 (내 컴퓨터 실행 시)
    win_font = "C:/Windows/Fonts/malgun.ttf"
    if os.path.exists(win_font):
        return ImageFont.truetype(win_font, size)
        
    # 🌟 3순위: 시스템 기본 Arial 시도
    try:
        return ImageFont.truetype("arial.ttf", size)
    except:
        # 최후의 수단 (크기 조절 안 됨)
        return ImageFont.load_default()

# --- 5. 실행 로직 ---

if st.session_state.menu == "🔍 규격 검수":
    st.header("🔍 GFA 광고 규격 검수")
    selected_ad = st.sidebar.selectbox("검수할 규격 선택", list(AD_SPECS.keys()))
    spec = AD_SPECS[selected_ad]
    uploaded_check = st.file_uploader(f"[{selected_ad}] 이미지 업로드", type=['jpg', 'png', 'jpeg'], key="check")
    
    if uploaded_check:
        img = Image.open(uploaded_check)
        w, h = img.size
        col1, col2 = st.columns([1.5, 1])
        with col2:
            if w == spec['w'] and h == spec['h']:
                st.success(f"✅ 규격 일치! ({w}x{h})")
            else:
                st.error(f"❌ 규격 불일치 (현재: {w}x{h} / 권장: {spec['w']}x{spec['h']})")
                if st.button("🔄 리사이징"):
                    resized = img.resize((spec['w'], spec['h']), Image.Resampling.LANCZOS)
                    buf = io.BytesIO()
                    resized.convert("RGB").save(buf, format="JPEG", quality=90)
                    st.download_button("📥 다운로드", buf.getvalue(), "fixed.jpg", "image/jpeg")
        with col1:
            st.image(img, use_container_width=True)

elif st.session_state.menu == "🎨 문구 합성":
    st.header("🎨 문구 합성 편집기")
    
    selected_gen = st.sidebar.selectbox("제작 규격 선택", list(AD_SPECS.keys()))
    gen_spec = AD_SPECS[selected_gen]
    
    uploaded_bg = st.sidebar.file_uploader("배경 이미지 불러오기", type=['jpg', 'png', 'jpeg'], key="bg")
    
    ad_text = st.sidebar.text_input("합성할 문구 입력", "야, 너도 GFA 할 수 있어!")
    text_color = st.sidebar.color_picker("글씨 색상 선택", "#FFFFFF")
    
    # 🌟 글자 크기 슬라이더 (최대 2000까지 확장)
    text_size = st.sidebar.slider("글자 크기 조절", 10, 2000, 200)
    
    if uploaded_bg:
        bg_img = Image.open(uploaded_bg).convert("RGB")
        canvas = bg_img.resize((gen_spec['w'], gen_spec['h']), Image.Resampling.LANCZOS)
        draw = ImageDraw.Draw(canvas)
        
        # 폰트 적용 (슬라이더 값 반영)
        font = get_font(text_size)
        
        # 정중앙 합성
        draw.text((gen_spec['w']//2, gen_spec['h']//2), ad_text, fill=text_color, font=font, anchor="mm")
        
        st.subheader("📷 미리보기")
        st.image(canvas, use_container_width=True)
        
        # 다운로드
        buf = io.BytesIO()
        canvas.save(buf, format="JPEG", quality=95)
        st.download_button("📥 완성된 이미지 다운로드", buf.getvalue(), "gfa_ad.jpg", "image/jpeg", use_container_width=True)
    else:
        st.info("왼쪽 사이드바에서 이미지를 먼저 업로드해 주세요.")
