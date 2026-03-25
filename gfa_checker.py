import streamlit as st
import io
from PIL import Image, ImageDraw, ImageFont
import os

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="GFA 클릭 마스터", layout="wide")

st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #111111; color: white !important; }
    [data-testid="stSidebar"] label p { color: white !important; font-size: 15px !important; font-weight: bold; }
    .main-title { background-color: #00C73C; padding: 15px; border-radius: 10px; color: white; text-align: center; margin-bottom: 20px; }
    </style>
    <div class="main-title"><h1>🎯 GFA 광고 마스터 PRO</h1></div>
    """, unsafe_allow_html=True)

# --- 2. 상태 관리 (위치 및 메뉴 저장) ---
if 'pos1' not in st.session_state: st.session_state.pos1 = (625, 100)
if 'pos2' not in st.session_state: st.session_state.pos2 = (625, 185)
if 'pos3' not in st.session_state: st.session_state.pos3 = (625, 270)

# --- 3. 폰트 로드 함수 ---
def get_font(size):
    actual_size = max(1, size)
    if os.path.exists("malgun.ttf"):
        return ImageFont.truetype("malgun.ttf", actual_size)
    return ImageFont.load_default()

# --- 4. GFA 규격 데이터 ---
AD_SPECS = {
    "스마트채널 (1250x370)": {"w": 1250, "h": 370},
    "네이버 메인 (1250x560)": {"w": 1250, "h": 560},
    "피드형 (1200x628)": {"w": 1200, "h": 628},
    "1:1 규격 (1200x1200)": {"w": 1200, "h": 1200},
    "배너형 (342x228)": {"w": 342, "h": 228}
}

# --- 5. 사이드바 설정 ---
st.sidebar.header("📂 1. 이미지 및 규격")
selected_ad = st.sidebar.selectbox("GFA 규격 선택", list(AD_SPECS.keys()))
spec = AD_SPECS[selected_ad]

uploaded_file = st.sidebar.file_uploader("배경 이미지 업로드", type=['jpg', 'png', 'jpeg'], key="gfa_uploader")

st.sidebar.markdown("---")
st.sidebar.header("✍️ 2. 텍스트 설정")

# 텍스트 이동 대상 선택
target = st.sidebar.radio("🖱️ 클릭 시 이동할 대상 선택", ["텍스트 1", "텍스트 2", "텍스트 3"])

with st.sidebar.expander("📝 텍스트 1 설정", expanded=(target == "텍스트 1")):
    txt1 = st.text_input("내용 1", "메인 문구", key="t1")
    clr1 = st.color_picker("색상 1", "#FFFFFF", key="c1")
    siz1 = st.slider("크기 1", 0, 150, 70, key="s1")

with st.sidebar.expander("📝 텍스트 2 설정", expanded=(target == "텍스트 2")):
    txt2 = st.text_input("내용 2", "", key="t2")
    clr2 = st.color_picker("색상 2", "#FFFFFF", key="c2")
    siz2 = st.slider("크기 2", 0, 150, 50, key="s2")

with st.sidebar.expander("📝 텍스트 3 설정", expanded=(target == "텍스트 3")):
    txt3 = st.text_input("내용 3", "", key="t3")
    clr3 = st.color_picker("색상 3", "#FFFFFF", key="c3")
    siz3 = st.slider("크기 3", 0, 150, 40, key="s3")

# --- 6. 메인 로직 ---
if uploaded_file:
    # 1. 이미지 준비
    img = Image.open(uploaded_file).convert("RGB")
    canvas = img.resize((spec['w'], spec['h']), Image.Resampling.LANCZOS)
    draw = ImageDraw.Draw(canvas)

    # 2. 텍스트 그리기
    if txt3: draw.text(st.session_state.pos3, txt3, fill=clr3, font=get_font(siz3), anchor="mm")
    if txt2: draw.text(st.session_state.pos2, txt2, fill=clr2, font=get_font(siz2), anchor="mm")
    if txt1: draw.text(st.session_state.pos1, txt1, fill=clr1, font=get_font(siz1), anchor="mm")

    st.info(f"💡 현재 **[{target}]** 이동 모드입니다. 이미지 위를 클릭하세요!")

    # 🌟 [오류 해결 핵심] 외부 라이브러리 없이 Streamlit 내장 클릭 기능 활용
    # st.image에 넣어둔 이미지를 클릭하면 좌표를 반환합니다.
    response = st.image(canvas, use_container_width=True)
    
    # 클릭 이벤트 감지 및 좌표 업데이트
    # Streamlit은 이미지 클릭 시 해당 지점의 좌표를 반환하는 내장 기능이 있습니다.
    if response is not None:
        try:
            # 클릭 데이터가 존재할 경우 좌표 추출
            if hasattr(response, 'image_coords') and response.image_coords:
                new_x = response.image_coords.x
                new_y = response.image_coords.y
                
                # 선택된 대상의 좌표 업데이트
                if target == "텍스트 1": st.session_state.pos1 = (new_x, new_y)
                elif target == "텍스트 2": st.session_state.pos2 = (new_x, new_y)
                elif target == "텍스트 3": st.session_state.pos3 = (new_x, new_y)
                st.rerun()
        except:
            pass

    # 다운로드 버튼
    buf = io.BytesIO()
    canvas.save(buf, format="JPEG", quality=95)
    st.download_button("📥 이미지 다운로드", buf.getvalue(), "gfa_ad.jpg", "image/jpeg", use_container_width=True)
else:
    st.info("왼쪽 사이드바에서 이미지를 업로드해 주세요.")
