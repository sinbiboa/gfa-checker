import streamlit as st
import io
from PIL import Image
import os

# --- 1. 페이지 설정 및 디자인 ---
st.set_page_config(page_title="GFA 실전 검수기", layout="wide")

st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #111111; color: white !important; }
    .main-title { background-color: #00C73C; padding: 20px; border-radius: 15px; color: white; text-align: center; margin-bottom: 30px; }
    .status-card { background-color: #ffffff; padding: 20px; border-radius: 10px; border: 1px solid #e1e4e8; margin-bottom: 20px; }
    .guide-box { background-color: #FFF5F5; padding: 20px; border-radius: 10px; border-left: 5px solid #FF4B4B; }
    .danger-text { color: #FF4B4B; font-weight: bold; }
    </style>
    <div class="main-title">
        <h1>🎯 GFA 실전 검수 & 규격 마스터</h1>
        <p>반려 1순위 사유 집중 체크 및 규격 최적화</p>
    </div>
    """, unsafe_allow_html=True)

# --- 2. GFA 규격 데이터 ---
AD_SPECS = {
    "스마트채널 (1250x370)": {"w": 1250, "h": 370},
    "네이버 메인 (1250x560)": {"w": 1250, "h": 560},
    "피드형 (1200x628)": {"w": 1200, "h": 628},
    "1:1 규격 (1200x1200)": {"w": 1200, "h": 1200},
    "배너형 (342x228)": {"w": 342, "h": 228}
}

# --- 3. 사이드바 ---
st.sidebar.header("📂 이미지 업로드")
selected_ad = st.sidebar.selectbox("검수 대상 규격", list(AD_SPECS.keys()))
spec = AD_SPECS[selected_ad]
uploaded_file = st.sidebar.file_uploader("이미지 파일을 선택하세요", type=['jpg', 'png', 'jpeg'])

# --- 4. 메인 실행 로직 ---
if uploaded_file:
    img = Image.open(uploaded_file)
    w, h = img.size
    
    col1, col2 = st.columns([1.5, 1])
    
    with col1:
        st.subheader("📷 규격 자동 최적화")
        if w == spec['w'] and h == spec['h']:
            st.success(f"✅ 규격 통과 ({w}x{h})")
            final_img = img
        else:
            st.warning(f"⚠️ 규격 자동 수정 ({w}x{h} → {spec['w']}x{spec['h']})")
            final_img = img.resize((spec['w'], spec['h']), Image.Resampling.LANCZOS)
        
        st.image(final_img, use_container_width=True)
        
        buf = io.BytesIO()
        final_img.convert("RGB").save(buf, format="JPEG", quality=95)
        st.download_button("📥 GFA 규격 완료 이미지 다운로드", buf.getvalue(), f"GFA_READY_{spec['w']}x{spec['h']}.jpg", "image/jpeg", use_container_width=True)

    with col2:
        st.subheader("🚨 반려 주의! 보류 확률 90% 항목")
        st.markdown(f"""
        <div class="guide-box">
            <p class="danger-text">⚠️ 아래 항목 중 하나라도 해당하면 보류됩니다.</p>
            <hr>
            <p><strong>1. 텍스트 면적 20% 초과</strong><br>
            글자가 이미지의 1/5보다 많으면 가독성 저하로 무조건 보류입니다.</p>
            <p><strong>2. '최저가/1위' 단독 사용</strong><br>
            근거(출처/날짜) 없는 최상급 표현은 반려 대상입니다. (예: 2024 네이버 검색량 기준 필수)</p>
            <p><strong>3. 낚시성 UI (X버튼, 마우스)</strong><br>
            이미지에 닫기(X) 버튼, 가짜 재생버튼, 마우스 커서가 그려져 있으면 100% 반려입니다.</p>
            <p><strong>4. 자극적인 비교 (Before/After)</strong><br>
            사용 전/후의 극단적인 대조나 혐오감을 주는 신체 부위 노출은 즉시 보류됩니다.</p>
            <p><strong>5. 저화질 및 깨짐</strong><br>
            원본이 작아 억지로 늘린 이미지(계단현상)는 반려됩니다.</p>
        </div>
        """, unsafe_allow_html=True)

    # --- 5. 하단 핵심 요약 ---
    st.markdown("---")
    st.subheader("📋 GFA 검수 패스 핵심 체크리스트")
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.info("**✅ 이미지 품질**\n- RGB 모드 확인\n- JPG 형식 확인\n- 왜곡 없는 고화질")
    with c2:
        st.info("**✅ 문구 및 텍스트**\n- 폰트 크기 식별 가능 여부\n- 배경색과 글자색 대비 명확\n- 오타 및 맞춤법 체크")
    with c3:
        st.info("**✅ 랜딩페이지**\n- 이미지 내용과 랜딩 내용 일치\n- 성인물/도박 등 불법 컨텐츠 확인")

else:
    st.info("왼쪽 사이드바에서 이미지를 업로드하면 즉시 검수 및 보류 사유 체크가 시작됩니다.")
