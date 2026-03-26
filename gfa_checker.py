import streamlit as st
import io
from PIL import Image
import google.generativeai as genai

# --- 1. API 설정 (사용 중인 키 그대로) ---
API_KEY = "AIzaSyCV2TYtxvw3JOo8-uGPQjm2ukHaqqxaguY"

@st.cache_resource
def configure_genai():
    try:
        genai.configure(api_key=API_KEY)
        # 🌟 해결 포인트: 'models/' 접두사를 붙여서 경로를 명시적으로 지정합니다.
        # 이렇게 하면 v1beta 에러를 피하고 표준 경로(v1)를 찾을 확률이 높습니다.
        return genai.GenerativeModel('models/gemini-1.5-flash')
    except Exception as e:
        st.error(f"모델 설정 중 오류: {e}")
        return None

model = configure_genai()

# --- 2. 페이지 설정 및 디자인 ---
st.set_page_config(page_title="GFA Gemini AI 검수기", layout="wide")

st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #111111; color: white !important; }
    .main-title { 
        background-color: #00C73C; padding: 20px; border-radius: 15px; 
        color: white; text-align: center; margin-bottom: 30px; 
    }
    .report-container {
        background-color: #f8f9fa; padding: 25px; border-radius: 12px;
        border-left: 6px solid #00C73C; line-height: 1.6; color: #333;
        white-space: pre-wrap;
    }
    </style>
    <div class="main-title">
        <h1>🎯 Gemini 실시간 GFA 검수 AI</h1>
        <p>네이버 GFA 4대 보류 사유를 정밀 분석합니다.</p>
    </div>
    """, unsafe_allow_html=True)

# --- 3. 사이드바 구성 ---
st.sidebar.header("📂 이미지 업로드")
uploaded_file = st.sidebar.file_uploader("검수할 이미지를 선택하세요", type=['jpg', 'png', 'jpeg'])

# --- 4. 메인 실행 로직 ---
if uploaded_file:
    img = Image.open(uploaded_file)
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📷 업로드 이미지")
        st.image(img, use_container_width=True)

    with col2:
        st.subheader("🤖 Gemini 실시간 분석")
        
        if model is None:
            st.error("AI 모델 로드 실패. API 키를 확인해 주세요.")
        else:
            with st.spinner("이미지를 정밀 분석 중입니다..."):
                try:
                    # 분석 프롬프트
                    prompt = "이 광고 이미지에서 네이버 GFA 보류 사유(개인정보 노출, UI 사칭, 가독성 부족)가 있는지 꼼꼼하게 분석해줘."
                    
                    # 🌟 이미지 데이터를 명시적으로 전송 (v1beta 충돌 방지)
                    response = model.generate_content([prompt, img])
                    
                    if response.text:
                        st.markdown(f'<div class="report-container">{response.text}</div>', unsafe_allow_html=True)
                    else:
                        st.warning("분석 결과가 비어있습니다.")
                except Exception as e:
                    # 404 에러가 나면 여기서 상세 메시지를 보여줍니다.
                    st.error(f"분석 중 오류 발생: {e}")
                    st.info("💡 해결 방법: Streamlit Cloud 대시보드에서 앱을 'Delete' 하신 후 'New app'으로 다시 만들어 보세요.")

else:
    st.info("이미지를 업로드하면 Gemini AI가 분석을 시작합니다.")
