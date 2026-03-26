import streamlit as st
import io
from PIL import Image
import google.generativeai as genai

# --- 1. Gemini API 설정 (키 적용) ---
API_KEY = "AIzaSyDhMcwOUTdBiaXFQKE0G4SYQ5189iKs_iA"

# 에러 방지를 위해 초기 모델 변수 설정
model = None

try:
    genai.configure(api_key=API_KEY)
    # 모델명을 풀네임으로 시도 (버전 호환성 확보)
    model = genai.GenerativeModel('models/gemini-1.5-flash')
except Exception as e:
    st.error(f"AI 모델 초기화 중 오류가 발생했습니다: {e}")

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
        <p>네이버 GFA 4대 보류 사유를 실시간으로 정밀 분석합니다.</p>
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
selected_ad = st.sidebar.selectbox("검토할 GFA 규격 선택", list(AD_SPECS.keys()))
spec = AD_SPECS[selected_ad]
uploaded_file = st.sidebar.file_uploader("검수할 이미지를 선택하세요", type=['jpg', 'png', 'jpeg'])

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
        st.download_button("📥 GFA 최적화 이미지 다운로드", buf.getvalue(), "GFA_READY.jpg", "image/jpeg", use_container_width=True)

    with col2:
        st.subheader("🤖 Gemini AI 분석 리포트")
        
        if model is None:
            st.error("AI 모델이 설정되지 않았습니다. API 키와 라이브러리 버전을 확인해 주세요.")
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
                    
                    # 🌟 콘텐츠 생성 시도
                    response = model.generate_content([prompt, img])
                    
                    if response:
                        st.markdown(f'<div class="report-container">{response.text}</div>', unsafe_allow_html=True)
                    else:
                        st.error("AI 응답을 받지 못했습니다.")
                        
                except Exception as e:
                    st.error(f"AI 분석 중 오류 발생: {e}")
                    st.write("라이브러리 버전 문제일 수 있습니다. 'requirements.txt'의 버전을 높여보세요.")

else:
    st.info("이미지를 업로드하면 Gemini AI가 분석을 시작합니다.")
