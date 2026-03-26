import streamlit as st
import io
from PIL import Image
import google.generativeai as genai

# --- 1. Gemini API 설정 (발급받은 키 적용) ---
API_KEY = "AIzaSyDhMcwOUTdBiaXFQKE0G4SYQ5189iKs_iA"

@st.cache_resource
def load_old_gemini_model():
    try:
        genai.configure(api_key=API_KEY)
        # 🌟 구버전에서 가장 안정적인 비전 모델명 사용
        return genai.GenerativeModel('gemini-pro-vision')
    except Exception as e:
        st.error(f"모델 초기화 오류: {e}")
        return None

model = load_old_gemini_model()

# --- 2. 페이지 설정 및 디자인 ---
st.set_page_config(page_title="GFA Gemini 검수 (구버전)", layout="wide")

st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #111111; color: white !important; }
    .main-title { 
        background-color: #0078FF; padding: 20px; border-radius: 15px; 
        color: white; text-align: center; margin-bottom: 30px; 
    }
    .report-container {
        background-color: #f8f9fa; padding: 20px; border-radius: 10px;
        border-left: 5px solid #0078FF; line-height: 1.6; color: #333;
        white-space: pre-wrap;
    }
    </style>
    <div class="main-title">
        <h1>🎯 Gemini GFA 검수 AI (안정화 버전)</h1>
        <p>호환성이 높은 구버전 모델(gemini-pro-vision)로 분석을 진행합니다.</p>
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
        st.subheader("📷 규격 최적화")
        final_img = img.resize((spec['w'], spec['h']), Image.Resampling.LANCZOS)
        st.image(final_img, use_container_width=True)
        
        buf = io.BytesIO()
        final_img.convert("RGB").save(buf, format="JPEG", quality=95)
        st.download_button("📥 다운로드", buf.getvalue(), "GFA_READY.jpg", "image/jpeg", use_container_width=True)

    with col2:
        st.subheader("🤖 AI 분석 리포트")
        
        if model is None:
            st.error("AI 모델 설정 실패. API 키를 확인해주세요.")
        else:
            with st.spinner("구버전 모델이 이미지를 분석 중입니다..."):
                try:
                    prompt = """
                    너는 네이버 GFA 광고 검수 전문가야. 이 이미지를 보고 '보류' 사유를 분석해줘.
                    1. 개인정보 노출 (이메일, 실명, 전화번호)
                    2. UI 사칭 (네이버 메일함 양식 등)
                    3. 가독성 (텍스트 크기)
                    4. 구성 (문서 노출 정도)
                    항목별로 설명해주고, 문제가 없으면 승인 가능하다고 말해줘.
                    """
                    
                    # 🌟 gemini-pro-vision 모델 호출 방식
                    response = model.generate_content([prompt, img])
                    
                    if response.text:
                        st.markdown(f'<div class="report-container">{response.text}</div>', unsafe_allow_html=True)
                    else:
                        st.warning("분석 결과가 비어있습니다.")
                        
                except Exception as e:
                    st.error(f"분석 중 오류 발생: {e}")
                    st.info("이 에러가 계속되면 API 키를 새로 발급받는 것을 추천합니다.")

else:
    st.info("이미지를 업로드하면 구버전 Gemini AI가 분석을 시작합니다.")
