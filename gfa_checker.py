import streamlit as st
import io
from PIL import Image
import os

# --- 1. 페이지 설정 및 디자인 ---
st.set_page_config(page_title="GFA 검수 마스터", layout="wide")

st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #111111; color: white !important; }
    .main-title { background-color: #00C73C; padding: 20px; border-radius: 15px; color: white; text-align: center; margin-bottom: 30px; }
    .status-card { background-color: #ffffff; padding: 20px; border-radius: 10px; border: 1px solid #e1e4e8; margin-bottom: 20px; box-shadow: 0px 4px 6px rgba(0,0,0,0.05); }
    .guide-box { background-color: #FFF5F5; padding: 20px; border-radius: 10px; border-left: 5px solid #FF4B4B; }
    .check-title { font-weight: 800; color: #FF4B4B; margin-bottom: 10px; font-size: 18px; }
    </style>
    <div class="main-title">
        <h1>🎯 GFA 광고 규격 검수 & 패스 가이드</h1>
        <p>이미지 규격 자동 수정 및 네이버 검수 보류 방지 체크리스트</p>
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

# --- 3. 사이드바 ---
st.sidebar.header("📂 이미지 업로드")
selected_ad = st.sidebar.selectbox("검토할 GFA 규격 선택", list(AD_SPECS.keys()))
spec = AD_SPECS[selected_ad]

uploaded_file = st.sidebar.file_uploader("이미지를 드래그하거나 선택하세요", type=['jpg', 'png', 'jpeg'])

# --- 4. 메인 실행 로직 ---
if uploaded_file:
    img = Image.open(uploaded_file)
    w, h = img.size
    
    col1, col2 = st.columns([1.5, 1])
    
    with col1:
        st.subheader("📷 이미지 규격 확인")
        # 규격 판정 및 자동 수정
        if w == spec['w'] and h == spec['h']:
            st.success(f"✅ 규격이 정확합니다! ({w}x{h})")
            final_img = img
        else:
            st.warning(f"⚠️ 규격 불일치 (현재: {w}x{h} → 권장: {spec['w']}x{spec['h']})")
            st.info("이미지를 규격에 맞게 자동 리사이징했습니다.")
            final_img = img.resize((spec['w'], spec['h']), Image.Resampling.LANCZOS)
        
        st.image(final_img, use_container_width=True)
        
        # 다운로드 버튼
        buf = io.BytesIO()
        final_img.convert("RGB").save(buf, format="JPEG", quality=95)
        st.download_button(
            label="📥 GFA 최적화 이미지 다운로드 (JPG)",
            data=buf.getvalue(),
            file_name=f"GFA_READY_{spec['w']}x{spec['h']}.jpg",
            mime="image/jpeg",
            use_container_width=True
        )

    with col2:
        st.subheader("🚩 검수 보류(반려) 자가진단")
        st.markdown(f"""
        <div class="guide-box">
            <div class="check-title">💡 이 이미지는 패스할 수 있을까요?</div>
            <p><strong>1. 텍스트 비중 체크 (20% 룰)</strong><br>
            문구가 이미지 전체의 1/5 이상을 차지하나요? 과도한 텍스트는 반려 1순위입니다.</p>
            <p><strong>2. 선정성 및 자극성</strong><br>
            신체 특정 부위 확대나 비포/애프터 비교 이미지가 포함되었나요? 무조건 보류됩니다.</p>
            <p><strong>3. 네이버 UI 사칭</strong><br>
            이미지 안에 'X' 버튼이나 알림창 아이콘이 있나요? 사용자 기만으로 판단되어 반려됩니다.</p>
            <p><strong>4. 저화질 및 왜곡</strong><br>
            글자가 깨져 보이거나 이미지가 억지로 늘어난 느낌인가요? 가독성 저하로 보류됩니다.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("### 📊 규격 상세 정보")
        st.write(f"- **대상:** {selected_ad}")
        st.write(f"- **권장 해상도:** {spec['w']} x {spec['h']} px")
        st.write(f"- **파일 형식:** JPG (RGB 모드)")
        st.write(f"- **용량:** 500KB 이하 권장")

    # --- 5. 하단 상세 보류 사유 요약 테이블 ---
    st.markdown("---")
    st.subheader("📋 GFA 검수 보류 주요 사유 요약")
    
    table_data = {
        "구분": ["텍스트 가독성", "이미지 품질", "표현 및 문구", "랜딩페이지"],
        "주요 보류 사유": [
            "폰트가 너무 작아 인식이 어렵거나 배경색과 대비가 약한 경우",
            "흰색 여백이 너무 많거나(Letterbox), 부자연스러운 합성 흔적",
            "'최저가', '전국 1위' 등 근거 없는 최상급 표현 사용 시",
            "광고 이미지의 내용과 클릭 후 연결되는 페이지 내용이 다른 경우"
        ]
    }
    st.table(table_data)

else:
    st.info("왼쪽 사이드바에서 이미지를 업로드해 주세요. GFA 규격에 맞춰 즉시 검수해 드립니다.")
