import streamlit as st
import io
from PIL import Image
import google.generativeai as genai

# --- 1. Gemini API 설정 (보내주신 키 적용) ---
API_KEY = "AIzaSyDhMcwOUTdBiaXFQKE0G4SYQ5189iKs_iA"

try:
    genai.configure(api_key=API_KEY)
    # 모델명을 'gemini-1.5-flash-latest'로 변경하여 경로 오류 방지
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
except Exception as e:
    st.error(f"API 설정 초기화 오류: {e}")

# --- 2. 페이지 설정 및 디자인 ---
st.set_page_config(page_title="GFA Gemini 검수 AI", layout="wide")

st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #111111; color: white !important; }
    .main-title { 
        background-color: #00C73C; 
        padding: 20px; 
        border-radius: 15px; 
        color: white; 
        text-align: center; 
        margin-bottom: 30px; 
    }
    .report-container {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #00C73C;
        line-height: 1.6;
        color: #333;
        white-space: pre-wrap; /* 줄바꿈 유지 */
    }
    </style>
    <div class="main-title">
        <h1>🎯 Gemini 실시간 GFA 검수 AI</h1>
        <p>최신 Gemini 1.5 Flash 모델로 실시간 검수를 진행합니다.</p>
    </div>
    """, unsafe_allow_html=True)

# --- 3. GFA 5대 규격 데이터 ---
AD_SPECS = {
    "스마트채널 (1250x370)": {"w": 1250, "h": 370},
    "네이버 메인 (1250x560)": {"w": 1250, "h": 560},
    "피드형 (1200x628)": {"w": 1200, "h": 628},
    "1:1 규격 (1200x1200)": {"w": 1200, "h": 1200},
    "배너형 (342x228)": {"w": 342, "h": 228}
}

# --- 4. 사이드바 구성 ---
st.sidebar.header("📂 이미지 업로드")
selected_ad = st.sidebar.selectbox("검토할 GFA 규격 선택", list(AD_SPECS.keys()))
spec = AD_SPECS[selected_ad]

uploaded_file = st.sidebar.file_uploader("검수할 이미지를 선택하세요", type=['jpg', 'png', 'jpeg'])

# --- 5. 메인 실행 로직 ---
if uploaded_file:
    img = Image.open(uploaded_file)
    
    col1, col2 = st.columns([1.5, 1])
    
    with col1:
        st.subheader("📷 규격 최적화 미리보기")
        final_img = img.resize((spec['w'], spec['h']), Image.Resampling.LANCZOS)
        st.image(final_img, use_container_width=True)
        
        buf = io.BytesIO()
        final_img.convert("RGB").save(buf, format="JPEG", quality=95)
        st.download_button(
            label="📥 GFA 최적화 이미지 다운로드",
            data=buf.getvalue(),
            file_name=f"GFA_READY.jpg",
            mime="image/jpeg",
            use_container_width=True
        )

    with col2:
        st.subheader("🤖 Gemini AI 분석 리포트")
        
        with st.spinner("AI가 이미지를 정밀 분석 중입니다..."):
            try:
                # 분석 프롬프트
                prompt = """
                너는 네이버 GFA 광고 검수 전문가야. 이 이미지를 보고 '보류(반려)' 사유가 있는지 아주 깐깐하게 분석해줘.
                특히 아래 4가지 항목에 대해서만 집중해서 대답해줘:

                1. 개인정보 노출: 이메일 주소, 실명, 전화번호 등이 마스킹 없이 포함되어 있는가?
                2. UI 사칭: 네이버 메인, 메일함 양식 등을 그대로 써서 사용자를 기만하는가?
                3. 가독성: 텍스트가 너무 작거나 흐릿해서 식별이 어려운가?
                4. 구성: 문서 전체가 노출되어 시선이 너무 분산되는가?

                각 항목별로 [심각], [주의], [경고], [안내] 태그를 붙여 설명해주고, 문제가 없다면 '승인 가능'하다고 말해줘.
                """
                
                # 콘텐츠 생성 호출
                response = model.generate_content([prompt, img])
                
                if response.text:
                    st.markdown(f'<div class="report-container">{response.text}</div>', unsafe_allow_html=True)
                else:
                    st.error("AI가 분석 결과를 생성하지 못했습니다. 다시 시도해 주세요.")
                
            except Exception as e:
                st.error(f"AI 분석 중 오류가 발생했습니다: {e}")
                st.info("Tip: 'requirements.txt'에서 'google-generativeai' 버전이 최신인지 확인해 보세요.")

else:
    st.info("이미지를 업로드하면 Gemini AI가 분석을 시작합니다.")
