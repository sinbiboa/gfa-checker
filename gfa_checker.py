import streamlit as st
import io
from PIL import Image
import google.generativeai as genai

# --- 1. Gemini API 설정 (최신 키 적용) ---
API_KEY = "AIzaSyCV2TYtxvw3JOo8-uGPQjm2ukHaqqxaguY"

@st.cache_resource
def load_stable_model():
    """404 에러를 방지하기 위해 가장 안정적인 호출 경로를 사용합니다."""
    try:
        genai.configure(api_key=API_KEY)
        
        # 🌟 해결 포인트: 'models/' 접두사를 명시하거나 가장 호환성 높은 경로 사용
        # 일부 환경에서는 'gemini-1.5-flash' 보다 'models/gemini-1.5-flash'가 정확합니다.
        model = genai.GenerativeModel('models/gemini-1.5-flash')
        return model, "Gemini 1.5 Flash (Standard)"
    except:
        try:
            # 🌟 대안: 구형 비전 모델 시도
            model = genai.GenerativeModel('models/gemini-pro-vision')
            return model, "Gemini Pro Vision (Legacy)"
        except Exception as e:
            return None, str(e)

model, active_info = load_stable_model()

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

# --- 3. 사이드바 구성 ---
st.sidebar.header("📂 이미지 업로드")
AD_SPECS = {
    "스마트채널 (1250x370)": {"w": 1250, "h": 370},
    "네이버 메인 (1250x560)": {"w": 1250, "h": 560},
    "피드형 (1200x628)": {"w": 1200, "h": 628},
    "1:1 규격 (1200x1200)": {"w": 1200, "h": 1200},
    "배너형 (342x228)": {"w": 342, "h": 228}
}
selected_ad = st.sidebar.selectbox("검토할 GFA 규격", list(AD_SPECS.keys()))
spec = AD_SPECS[selected_ad]
uploaded_file = st.sidebar.file_uploader("검수할 이미지를 선택하세요", type=['jpg', 'png', 'jpeg'])

if active_info:
    st.sidebar.success(f"🤖 연결 상태: {active_info}")
else:
    st.sidebar.error(f"❌ 연결 실패: {active_info}")

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
            st.error("AI 모델을 불러올 수 없습니다. API 키를 새로 발급받거나 서버를 재부팅해 보세요.")
        else:
            with st.spinner("AI가 이미지를 정밀 분석 중입니다..."):
                try:
                    prompt = """
                    너는 네이버 GFA 광고 검수 전문가야. 이 이미지를 보고 '보류' 사유가 있는지 분석해줘.
                    1. 개인정보 노출 (이메일, 실명, 전화번호)
                    2. UI 사칭 (네이버 메일함 양식 등)
                    3. 가독성 (텍스트 크기)
                    4. 구성 (문서 노출 정도)
                    항목별로 [심각], [주의], [경고], [안내] 태그를 붙여 설명해주고, 문제가 없으면 승인 가능하다고 말해줘.
                    """
                    
                    # 🌟 이미지 데이터를 명시적으로 전송
                    response = model.generate_content([prompt, img])
                    
                    if response.text:
                        st.markdown(f'<div class="report-container">{response.text}</div>', unsafe_allow_html=True)
                    else:
                        st.warning("분석 결과가 비어있습니다. 다시 시도해 주세요.")
                except Exception as e:
                    st.error(f"분석 중 오류 발생: {e}")

else:
    st.info("이미지를 업로드하면 Gemini AI가 분석을 시작합니다.")
