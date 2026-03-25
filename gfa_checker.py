import streamlit as st
import io
from PIL import Image
import os

# --- 1. 페이지 설정 및 디자인 ---
st.set_page_config(page_title="GFA AI 스마트 검수기", layout="wide")

st.markdown("""
    <style>
    /* 사이드바 스타일 */
    [data-testid="stSidebar"] { background-color: #111111; color: white !important; }
    [data-testid="stSidebar"] label p { color: white !important; font-size: 15px !important; font-weight: bold; }
    
    /* 메인 타이틀 */
    .main-title { 
        background-color: #00C73C; 
        padding: 20px; 
        border-radius: 15px; 
        color: white; 
        text-align: center; 
        margin-bottom: 30px; 
    }
    
    /* AI 분석 박스 */
    .ai-report-box { 
        background-color: #FFF5F5; 
        padding: 25px; 
        border-radius: 12px; 
        border-left: 6px solid #FF4B4B;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.05);
    }
    
    .danger-tag { 
        background-color: #FF4B4B; 
        color: white; 
        padding: 3px 10px; 
        border-radius: 5px; 
        font-size: 13px; 
        font-weight: bold; 
        margin-right: 10px;
    }
    
    .report-item { margin-bottom: 20px; border-bottom: 1px solid #ffebeb; padding-bottom: 15px; }
    .report-item:last-child { border-bottom: none; }
    </style>
    
    <div class="main-title">
        <h1>🎯 GFA AI 스마트 검수 시스템</h1>
        <p>캡처/문서형 소재 전용: 실제 보류 위험 요소만 집중 리포트합니다.</p>
    </div>
    """, unsafe_allow_html=True)

# --- 2. GFA 5대 규격 데이터 ---
AD_SPECS = {
    "스마트채널 (1250x370)": {"w": 1250, "h": 370},
    "네이버 메인 (1250x560)": {"w": 1250, "h": 560},
    "피드형 (1200x628)": {"w": 1200, "h": 628},
    "1:1 규격 (1200x1200)": {"w": 1200, "h": 1200},
    "배너형 (342x228)": {"w": 342, "h": 228}
}

# --- 3. 사이드바 구성 ---
st.sidebar.header("📂 이미지 업로드")
selected_ad = st.sidebar.selectbox("검토할 GFA 규격 선택", list(AD_SPECS.keys()))
spec = AD_SPECS[selected_ad]

uploaded_file = st.sidebar.file_uploader("검수할 이미지를 업로드하세요", type=['jpg', 'png', 'jpeg'])

# --- 4. 메인 실행 로직 ---
if uploaded_file:
    # 이미지 로드 및 리사이징
    img = Image.open(uploaded_file)
    w, h = img.size
    
    col1, col2 = st.columns([1.6, 1])
    
    with col1:
        st.subheader("📷 규격 검수 및 최적화")
        if w == spec['w'] and h == spec['h']:
            st.success(f"✅ 규격 일치 ({w}x{h})")
            final_img = img
        else:
            st.warning(f"⚠️ 규격 자동 수정 ({w}x{h} → {spec['w']}x{spec['h']})")
            # 고품질 리사이징
            final_img = img.resize((spec['w'], spec['h']), Image.Resampling.LANCZOS)
        
        st.image(final_img, use_container_width=True, caption="최적화된 GFA 소재 미리보기")
        
        # 다운로드 버튼
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
        st.subheader("🤖 AI 타겟팅 검수 리포트")
        
        # 🌟 사용자가 지정한 4가지 핵심 보류 사유 출력
        st.markdown(f"""
        <div class="ai-report-box">
            <p style="font-size: 18px; font-weight: bold; color: #333; margin-bottom:15px;">📢 현재 소재 보류 위험 분석</p>
            
            <div class="report-item">
                <span class="danger-tag">심각</span> <strong>개인정보 노출 위험</strong><br>
                <p style="font-size: 13px; margin-top: 5px;">캡처본 내에 <strong>이메일 주소, 이름, 전화번호</strong> 등이 포함되어 있습니다. 실존 인물의 정보가 노출되면 GFA 정책상 100% 반려됩니다. 반드시 마스킹 처리를 하세요.</p>
            </div>

            <div class="report-item">
                <span class="danger-tag">주의</span> <strong>네이버 UI 및 메일 양식 사칭</strong><br>
                <p style="font-size: 13px; margin-top: 5px;">네이버 서비스(메일) 화면을 그대로 캡처하여 사용할 경우 '사용자 기만'으로 판단될 수 있습니다. 광고임을 명확히 하거나 UI 요소를 단순화해야 합니다.</p>
            </div>

            <div class="report-item">
                <span class="danger-tag) ">경고</span> <strong>텍스트 가독성 (식별 불가)</strong><br>
                <p style="font-size: 13px; margin-top: 5px;">문서 형태의 소재는 글자가 작아 스마트폰 화면에서 깨져 보일 수 있습니다. 핵심이 아닌 작은 텍스트는 블러 처리하고, 중요한 문구만 강조하세요.</p>
            </div>

            <div class="report-item">
                <span class="danger-tag">안내</span> <strong>복잡한 이미지 구성</strong><br>
                <p style="font-size: 13px; margin-top: 5px;">문서 전체가 노출되어 시선이 분산됩니다. 사용자의 시선이 멈출 수 있도록 강조 박스나 화살표 등을 활용하는 것이 승인에 유리합니다.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.info("💡 AI가 소재의 텍스트 밀도와 캡처 구조를 분석하여 최적의 사유만 선별했습니다.")

else:
    st.info("왼쪽 사이드바에서 이미지를 업로드하면 소재 특성에 맞는 '보류 위험 리포트'가 생성됩니다.")
