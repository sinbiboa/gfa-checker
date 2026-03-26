import streamlit as st
import io
from PIL import Image
import google.generativeai as genai

# --- 1. Gemini API 설정 ---
API_KEY = "AIzaSyCV2TYtxvw3JOo8-uGPQjm2ukHaqqxaguY"
genai.configure(api_key=API_KEY)

# 🌟 중요: 모델명을 'models/gemini-1.5-flash'로 풀네임을 써야 에러가 안 납니다.
model = genai.GenerativeModel('models/gemini-1.5-flash')

st.set_page_config(page_title="GFA 검수 AI", layout="wide")
st.markdown("<h1 style='text-align: center; color: #00C73C;'>🎯 GFA AI 실시간 검수</h1>", unsafe_allow_html=True)

uploaded_file = st.sidebar.file_uploader("이미지 선택", type=['jpg', 'png', 'jpeg'])

if uploaded_file:
    img = Image.open(uploaded_file)
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.image(img, use_container_width=True)
        
    with col2:
        st.subheader("🤖 AI 분석 리포트")
        with st.spinner("Gemini가 정밀 분석 중입니다..."):
            try:
                # 분석 실행
                prompt = "네이버 GFA 광고 가이드에 따라 이 이미지의 보류 사유(개인정보, UI사칭, 가독성)를 분석해줘."
                response = model.generate_content([prompt, img])
                st.info(response.text)
            except Exception as e:
                st.error(f"분석 중 오류 발생: {e}")
