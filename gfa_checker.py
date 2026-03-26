import streamlit as st
import io
from PIL import Image
import google.generativeai as genai

# --- 1. API 설정 (사용 중인 키 그대로) ---
API_KEY = "AIzaSyCV2TYtxvw3JOo8-uGPQjm2ukHaqqxaguY"
genai.configure(api_key=API_KEY)

# 🌟 404 에러 방지를 위해 'models/' 경로를 명시합니다.
model = genai.GenerativeModel('models/gemini-1.5-flash')

st.set_page_config(page_title="GFA 검수 AI", layout="wide")
st.markdown("<h1 style='text-align: center; color: #00C73C;'>🎯 GFA AI 실시간 검수</h1>", unsafe_allow_html=True)

uploaded_file = st.sidebar.file_uploader("검수할 이미지 선택", type=['jpg', 'png', 'jpeg'])

if uploaded_file:
    img = Image.open(uploaded_file)
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📷 업로드 이미지")
        st.image(img, use_container_width=True)
        
    with col2:
        st.subheader("🤖 Gemini 분석 결과")
        with st.spinner("AI가 이미지를 읽고 있습니다..."):
            try:
                # 분석 프롬프트
                prompt = "이 광고 이미지에서 네이버 GFA 보류 사유(개인정보, UI사칭, 가독성 문제)가 있는지 분석해줘."
                response = model.generate_content([prompt, img])
                st.info(response.text)
            except Exception as e:
                st.error(f"분석 중 오류 발생: {e}")
                st.write("💡 Tip: 오른쪽 하단 Manage app -> Reboot App을 실행해 보세요.")
