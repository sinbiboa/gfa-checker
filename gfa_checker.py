import streamlit as st
import io
from PIL import Image
import google.generativeai as genai

# --- 1. Gemini API 설정 (새로 주신 키 적용) ---
API_KEY = "AIzaSyCV2TYtxvw3JOo8-uGPQjm2ukHaqqxaguY"

@st.cache_resource
def load_best_model():
    """서버 환경에 맞는 최적의 모델을 자동으로 로드합니다."""
    genai.configure(api_key=API_KEY)
    
    # 시도할 모델 리스트 (우선순위 순)
    model_names = [
        'gemini-1.5-flash', 
        'gemini-pro-vision', 
        'gemini-1.5-flash-latest'
    ]
    
    for name in model_names:
        try:
            model = genai.GenerativeModel(name)
            # 모델이 정상 작동하는지 테스트 호출 대신 객체 생성 확인
            return model, name
        except:
            continue
    return None, None

model, active_model_name = load_best_model()

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
        white-space: pre-wrap; font-size: 15px;
    }
    </style>
    <div class="main-title">
        <h1>🎯 Gemini 실시간 GFA 검수 AI</h1>
        <p>네이버 GFA 4대 보류 사유를 정밀 분석합니다.</p>
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
uploaded_file = st.sidebar.file_uploader("검수할 이미지를 선택하세요", type=['jpg', 'png', 'jpeg'])

if active_model_name:
    st.sidebar.success(f"🤖 연결된 모델: {active_model_name}")
else:
    st.sidebar.error("❌ AI 모델 연결 실패")

# --- 4. 메인 로직 ---
if uploaded_file:
    img = Image.open(uploaded_file)
    col1, col2 = st.columns([1.5, 1])
    
    with col1:
        st.subheader("📷 규격 최적화 미리보기")
        final_img = img.resize((spec['w'], spec['h']), Image.Resampling.LANCZOS)
        st.image(final_img, use_container_width=True)
        
        buf = io.BytesIO()
        final_img.convert("RGB").save(buf, format="JPEG", quality=95)
        st.download_button("📥 GFA 최적화 이미지 다운로드", buf.getvalue(), "GFA_READY.jpg", "image/jpeg", use_container_width=True)

    with col2:
        st.subheader("🤖 Gemini 실시간 분석 리포트")
        
        if model is None:
            st.error("AI 모델을 불러올 수 없습니다. API 키 권한을 확인해주세요.")
        else:
            with st.spinner("AI가 이미지를 정밀 분석 중입니다..."):
                try:
                    prompt = """
                    너는 네이버 GFA 광고 검수 전문가야. 이 이미지를 보고 '보류' 사유가 있는지 분석해줘.
                    특히 아래 4가지 항목에 대해서만 집중해서 대답해줘:
                    1. 개인정보 노출: 이메일 주소, 실명, 전화번호 포함 여부
                    2. UI 사칭: 네이버 메일함 양식 등을 그대로 썼는지
                    3. 가독성: 텍스트가 식별 가능한 크기인지
                    4. 구성: 문서 노출이 과도하여 시선이 분산되는지
                    항목별로 [심각], [주의], [경고], [안내] 태그를 붙여 설명해주고, 문제가 없으면 승인 가능하다고 말해줘.
                    """
                    
                    response = model.generate_content([prompt, img])
                    
                    if response.text:
                        st.markdown(f'<div class="report-container">{response.text}</div>', unsafe_allow_html=True)
                    else:
                        st.warning("분석 결과가 비어있습니다. 다시 시도해주세요.")
                        
                except Exception as e:
                    st.error(f"분석 중 오류 발생: {e}")
                    st.info("이미지를 다시 업로드하거나 잠시 후 시도해보세요.")

else:
    st.info("이미지를 업로드하면 Gemini AI가 실시간 분석을 시작합니다.")
