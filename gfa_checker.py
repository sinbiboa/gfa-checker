import streamlit as st
import io
from PIL import Image
import google.generativeai as genai

# --- 1. Gemini API 설정 (발급받은 최신 키) ---
API_KEY = "AIzaSyCV2TYtxvw3JOo8-uGPQjm2ukHaqqxaguY"

# 모델 로드 방식을 캐싱하여 속도와 안정성 향상
@st.cache_resource
def load_model():
    try:
        genai.configure(api_key=API_KEY)
        # 🌟 404 에러 방지를 위해 가장 표준적인 모델명 사용
        model = genai.GenerativeModel('gemini-1.5-flash')
        return model
    except Exception as e:
        st.error(f"모델 초기화 오류: {e}")
        return None

model = load_model()

# --- 2. 페이지 설정 및 디자인 ---
st.set_page_config(page_title="GFA Gemini AI 검수기", layout="wide")

st.markdown("""
    <style>
    /* 사이드바 스타일 */
    [data-testid="stSidebar"] { background-color: #111111; color: white !important; }
    
    /* 메인 타이틀 */
    .main-title { 
        background-color: #00C73C; 
        padding: 20px; 
        border-radius: 15px; 
        color: white; 
        text-align: center; 
        margin-bottom: 30px; 
    }
    
    /* 분석 리포트 박스 */
    .report-box { 
        background-color: #f8f9fa; 
        padding: 25px; 
        border-radius: 12px; 
        border-left: 6px solid #00C73C;
        line-height: 1.8;
        color: #333;
        white-space: pre-wrap;
        font-size: 15px;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.05);
    }
    </style>
    
    <div class="main-title">
        <h1>🎯 Gemini 실시간 GFA 검수 AI</h1>
        <p>네이버 GFA 4대 보류 사유를 정밀 분석하여 리포트를 생성합니다.</p>
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

# --- 4. 사이드바 구성 ---
st.sidebar.header("📂 이미지 업로드")
selected_ad = st.sidebar.selectbox("검토할 GFA 규격 선택", list(AD_SPECS.keys()))
spec = AD_SPECS[selected_ad]

uploaded_file = st.sidebar.file_uploader("검수할 이미지를 업로드하세요", type=['jpg', 'png', 'jpeg'])

# --- 5. 메인 실행 로직 ---
if uploaded_file:
    # 이미지 열기
    img = Image.open(uploaded_file)
    w, h = img.size
    
    col1, col2 = st.columns([1.5, 1])
    
    with col1:
        st.subheader("📷 규격 최적화 미리보기")
        # 고품질 리사이징 실행
        final_img = img.resize((spec['w'], spec['h']), Image.Resampling.LANCZOS)
        st.image(final_img, use_container_width=True, caption=f"현재 규격: {spec['w']}x{spec['h']}")
        
        # 최적화 이미지 다운로드 버튼
        buf = io.BytesIO()
        final_img.convert("RGB").save(buf, format="JPEG", quality=95)
        st.download_button(
            label="📥 GFA 최적화 이미지 다운로드",
            data=buf.getvalue(),
            file_name=f"GFA_READY_{spec['w']}x{spec['h']}.jpg",
            mime="image/jpeg",
            use_container_width=True
        )

    with col2:
        st.subheader("🤖 Gemini 실시간 분석")
        
        if model is None:
            st.error("AI 모델을 불러오지 못했습니다. API 키를 확인하거나 앱을 다시 생성해 주세요.")
        else:
            with st.spinner("이미지를 정밀 분석 중입니다..."):
                try:
                    # 보류 사유 분석을 위한 맞춤형 프롬프트
                    prompt = """
                    너는 네이버 GFA 광고 검수 전문가야. 이 이미지를 보고 네이버 광고 가이드에 따라 '보류(반려)'될 사유가 있는지 아주 깐깐하게 분석해줘.
                    특히 아래 4가지 항목에 대해서만 집중해서 대답해줘:

                    1. **개인정보 노출**: 이메일 주소, 실명, 전화번호 등이 마스킹 없이 포함되어 있는가?
                    2. **UI 사칭**: 네이버 메인 화면이나 메일함 양식 등을 그대로 써서 사용자를 기만하는가?
                    3. **가독성**: 텍스트가 너무 작거나 흐릿해서 식별이 어려운가? (모바일 가독성)
                    4. **이미지 구성**: 문서 전체가 노출되어 시선이 분산되거나 정보가 과다한가?

                    각 항목별로 [심각], [주의], [경고], [안내] 태그를 붙여서 상세히 설명해주고, 
                    문제가 없다면 '승인 가능성이 매우 높습니다'라고 마무리해줘.
                    """
                    
                    # AI 분석 실행 (v1beta 에러 방지를 위한 표준 호출)
                    response = model.generate_content([prompt, img])
                    
                    if response.text:
                        st.markdown(f'<div class="report-box">{response.text}</div>', unsafe_allow_html=True)
                    else:
                        st.warning("분석 내용을 생성하지 못했습니다. 다시 시도해 주세요.")
                        
                except Exception as e:
                    st.error(f"분석 중 오류 발생: {e}")
                    st.info("💡 에러가 계속되면 Streamlit Cloud에서 앱을 삭제(Delete)한 후 새로 생성(New app)해 보세요.")

else:
    st.info("왼쪽 사이드바에서 이미지를 업로드하면 Gemini AI가 분석을 시작합니다.")
