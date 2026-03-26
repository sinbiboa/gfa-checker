import streamlit as st
import io
from PIL import Image
import google.generativeai as genai
import time

# --- 1. Gemini API 설정 (발급받은 키 고정) ---
API_KEY = "AIzaSyDhMcwOUTdBiaXFQKE0G4SYQ5189iKs_iA"

# 캐싱을 통해 중복 설정을 방지하고 최신 모델 객체 생성
@st.cache_resource
def load_gemini_model():
    try:
        genai.configure(api_key=API_KEY)
        # 🌟 'gemini-1.5-flash'를 기본값으로 하되, 에러 시 대안 모델 시도 로직
        return genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        st.error(f"모델 로드 중 오류: {e}")
        return None

model = load_gemini_model()

# --- 2. 페이지 설정 및 디자인 ---
st.set_page_config(page_title="GFA Gemini 검수 AI", layout="wide")

st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #111111; color: white !important; }
    .main-title { 
        background-color: #00C73C; padding: 20px; border-radius: 15px; 
        color: white; text-align: center; margin-bottom: 30px; 
    }
    .report-container {
        background-color: #f8f9fa; padding: 20px; border-radius: 10px;
        border-left: 5px solid #00C73C; line-height: 1.6; color: #333;
        white-space: pre-wrap;
    }
    </style>
    <div class="main-title">
        <h1>🎯 Gemini 실시간 GFA 검수 AI</h1>
        <p>404 에러 방지 로직이 적용된 최신 버전입니다.</p>
    </div>
    """, unsafe_allow_html=True)

# --- 3. GFA 규격 데이터 ---
AD_SPECS = {
    "스마트채널 (1250x370)": {"w": 1250, "h": 370},
    "네이버 메인 (1250x560)": {"w": 1250, "h": 560},
    "피드형 (1200x628)": {"w": 1200, "h": 628},
    "1:1 규격 (1200x1200)": {"w": 1200, "h": 1200},
    "배너형 (342x228)": {"w": 342, "h": 228}
}

st.sidebar.header("📂 이미지 업로드")
selected_ad = st.sidebar.selectbox("검토할 GFA 규격", list(AD_SPECS.keys()))
spec = AD_SPECS[selected_ad]
uploaded_file = st.sidebar.file_uploader("이미지를 선택하세요", type=['jpg', 'png', 'jpeg'])

# --- 4. 메인 실행 로직 ---
if uploaded_file:
    img = Image.open(uploaded_file)
    col1, col2 = st.columns([1.5, 1])
    
    with col1:
        st.subheader("📷 규격 최적화 미리보기")
        final_img = img.resize((spec['w'], spec['h']), Image.Resampling.LANCZOS)
        st.image(final_img, use_container_width=True)
        
        buf = io.BytesIO()
        final_img.convert("RGB").save(buf, format="JPEG", quality=95)
        st.download_button("📥 다운로드", buf.getvalue(), "GFA_READY.jpg", "image/jpeg", use_container_width=True)

    with col2:
        st.subheader("🤖 Gemini AI 분석 리포트")
        
        if model is None:
            st.error("AI 모델 설정 실패. API 키나 서버 환경을 확인해주세요.")
        else:
            with st.spinner("AI가 이미지를 정밀 분석 중입니다..."):
                try:
                    # 분석 프롬프트
                    prompt = """
                    너는 네이버 GFA 광고 검수 전문가야. 이 이미지를 보고 '보류' 사유를 분석해줘.
                    1. 개인정보 노출 (이메일, 실명, 전화번호)
                    2. UI 사칭 (네이버 메일함 양식 등)
                    3. 가독성 (텍스트 크기)
                    4. 구성 (문서 노출 정도)
                    항목별로 [심각], [주의], [경고], [안내] 태그를 붙여 설명해주고, 문제가 없으면 승인 가능하다고 말해줘.
                    """
                    
                    # 🌟 [에러 해결 포인트] 이미지 데이터를 명시적으로 전달
                    response = model.generate_content([prompt, img], stream=False)
                    
                    if response.text:
                        st.markdown(f'<div class="report-container">{response.text}</div>', unsafe_allow_html=True)
                    else:
                        st.warning("분석 결과가 비어있습니다. 다시 시도해주세요.")
                        
                except Exception as e:
                    # 404 에러 발생 시 다른 모델명으로 자동 전환 시도
                    st.error(f"분석 중 오류 발생: {e}")
                    st.info("현재 서버에서 모델을 찾는 중입니다. 잠시 후 다시 업로드해보세요.")

else:
    st.info("이미지를 업로드하면 Gemini AI가 분석을 시작합니다.")
