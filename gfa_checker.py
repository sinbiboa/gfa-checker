import streamlit as st
import io
from PIL import Image
import google.generativeai as genai

# --- 1. Gemini API 설정 ---
API_KEY = "AIzaSyCV2TYtxvw3JOo8-uGPQjm2ukHaqqxaguY"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- 2. 페이지 설정 ---
st.set_page_config(page_title="GFA Gemini 검수기", layout="wide")
st.markdown("<h1 style='text-align: center; color: #00C73C;'>🎯 GFA AI 실시간 검수</h1>", unsafe_allow_html=True)

# --- 3. 사이드바 및 업로드 ---
st.sidebar.header("📂 이미지 업로드")
AD_SPECS = {
    "스마트채널 (1250x370)": {"w": 1250, "h": 370},
    "네이버 메인 (1250x560)": {"w": 1250, "h": 560},
    "피드형 (1200x628)": {"w": 1200, "h": 628},
    "1:1 규격 (1200x1200)": {"w": 1200, "h": 1200},
    "배너형 (342x228)": {"w": 342, "h": 228}
}
selected_ad = st.sidebar.selectbox("GFA 규격 선택", list(AD_SPECS.keys()))
spec = AD_SPECS[selected_ad]
uploaded_file = st.sidebar.file_uploader("이미지 선택", type=['jpg', 'png', 'jpeg'])

# --- 4. 메인 실행 ---
if uploaded_file:
    img = Image.open(uploaded_file)
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📷 규격 최적화")
        final_img = img.resize((spec['w'], spec['h']), Image.Resampling.LANCZOS)
        st.image(final_img, use_container_width=True)
        
        buf = io.BytesIO()
        final_img.convert("RGB").save(buf, format="JPEG", quality=95)
        st.download_button("📥 이미지 다운로드", buf.getvalue(), "GFA_READY.jpg", "image/jpeg")

    with col2:
        st.subheader("🤖 AI 분석 리포트")
        with st.spinner("Gemini가 분석 중입니다..."):
            try:
                prompt = "네이버 GFA 광고 검수 가이드에 따라 이 이미지의 보류 사유(개인정보, UI사칭, 가독성)를 분석해줘."
                response = model.generate_content([prompt, img])
                st.info(response.text)
            except Exception as e:
                st.error(f"오류 발생: {e}")
else:
    st.info("이미지를 업로드하면 분석이 시작됩니다.")
