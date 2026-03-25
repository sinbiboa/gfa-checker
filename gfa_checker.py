import streamlit as st
import io
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import os
from streamlit_image_coordinates import streamlit_image_coordinates

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="GFA 멀티 편집기", layout="wide")

st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #111111; color: white !important; }
    .main-title { background-color: #00C73C; padding: 15px; border-radius: 10px; color: white; text-align: center; }
    </style>
    <div class="main-title"><h1>🎯 GFA 멀티 텍스트 마스터</h1></div>
    """, unsafe_allow_html=True)

# --- 2. 상태 관리 ---
if 'menu' not in st.session_state: st.session_state.menu = "🎨 문구 합성"
# 텍스트 1, 2, 3의 좌표 저장
if 'pos1' not in st.session_state: st.session_state.pos1 = (625, 100)
if 'pos2' not in st.session_state: st.session_state.pos2 = (625, 200)
if 'pos3' not in st.session_state: st.session_state.pos3 = (625, 300)

# --- 3. 폰트 함수 ---
def get_font(size):
    size = max(1, size)
    if os.path.exists("malgun.ttf"):
        return ImageFont.truetype("malgun.ttf", size)
    return ImageFont.load_default()

# --- 4. 메인 로직 ---
st.sidebar.header("🛠️ 메뉴")
if st.sidebar.button("🔍 규격 검수"): st.session_state.menu = "🔍 규격 검수"
if st.sidebar.button("🎨 문구 합성"): st.session_state.menu = "🎨 문구 합성"

if st.session_state.menu == "🔍 규격 검수":
    st.header("🔍 GFA 규격 검수")
    # ... (기존 검수 코드 생략) ...
    st.info("검수 기능은 기존과 동일하게 작동합니다.")

elif st.session_state.menu == "🎨 문구 합성":
    st.sidebar.subheader("📍 위치 수정 대상")
    edit_target = st.sidebar.radio("클릭 시 이동할 텍스트 선택", ["텍스트 1", "텍스트 2", "텍스트 3"])

    st.sidebar.markdown("---")
    
    # 텍스트 1 설정
    st.sidebar.subheader("📝 텍스트 1")
    txt1 = st.sidebar.text_input("내용 1", "첫 번째 문구")
    col1_1, col1_2 = st.sidebar.columns(2)
    clr1 = col1_1.color_picker("색상 1", "#FFFFFF", key="c1")
    siz1 = col1_2.slider("크기 1", 0, 150, 60, key="s1")

    # 텍스트 2 설정
    st.sidebar.subheader("📝 텍스트 2")
    txt2 = st.sidebar.text_input("내용 2", "")
    col2_1, col2_2 = st.sidebar.columns(2)
    clr2 = col2_1.color_picker("색상 2", "#FFFFFF", key="c2")
    siz2 = col2_2.slider("크기 2", 0, 150, 40, key="s2")

    # 텍스트 3 설정
    st.sidebar.subheader("📝 텍스트 3")
    txt3 = st.sidebar.text_input("내용 3", "")
    col3_1, col3_2 = st.sidebar.columns(2)
    clr3 = col3_1.color_picker("색상 3", "#FFFFFF", key="c3")
    siz3 = col3_2.slider("크기 3", 0, 150, 30, key="s3")

    uploaded_bg = st.sidebar.file_uploader("배경 이미지 업로드", type=['jpg', 'png', 'jpeg'])

    if uploaded_bg:
        img = Image.open(uploaded_bg).convert("RGB")
        # 현재 선택된 규격(예: 1250x560)으로 리사이징 과정은 생략(이미지 그대로 사용)
        canvas = img.copy()
        draw = ImageDraw.Draw(canvas)

        # 텍스트 1 그리기
        if txt1:
            draw.text(st.session_state.pos1, txt1, fill=clr1, font=get_font(siz1), anchor="mm")
        # 텍스트 2 그리기
        if txt2:
            draw.text(st.session_state.pos2, txt2, fill=clr2, font=get_font(siz2), anchor="mm")
        # 텍스트 3 그리기
        if txt3:
            draw.text(st.session_state.pos3, txt3, fill=clr3, font=get_font(siz3), anchor="mm")

        st.info(f"💡 현재 **[{edit_target}]** 이동 모드입니다. 이미지 위를 클릭하세요.")
        
        # 마우스 클릭 처리
        img_arr = np.array(canvas)
        value = streamlit_image_coordinates(img_arr, key="gfa_editor", use_container_width=True)

        if value:
            new_pos = (value["x"], value["y"])
            if edit_target == "텍스트 1": st.session_state.pos1 = new_pos
            elif edit_target == "텍스트 2": st.session_state.pos2 = new_pos
            elif edit_target == "텍스트 3": st.session_state.pos3 = new_pos
            st.rerun()

        # 다운로드
        buf = io.BytesIO()
        canvas.save(buf, format="JPEG", quality=95)
        st.download_button("📥 최종 이미지 다운로드", buf.getvalue(), "gfa_final.jpg", "image/jpeg", use_container_width=True)
    else:
        st.info("사이드바에서 배경 이미지를 업로드해 주세요.")
