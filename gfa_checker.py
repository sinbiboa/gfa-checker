import streamlit as st
import io
from PIL import Image
import os

# --- 1. 페이지 설정 및 디자인 ---
st.set_page_config(page_title="GFA 규격 마스터", layout="wide")

st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #111111; color: white !important; }
    [data-testid="stSidebar"] label p { color: white !important; font-size: 16px !important; font-weight: bold; }
    .main-title { background-color: #00C73C; padding: 20px; border-radius: 15px; color: white; text-align: center; margin-bottom: 30px; }
    </style>
    <div class="main-title">
        <h1>🎯 GFA 광고 규격 마스터</h1>
        <p>네이버 GFA 5대 필수 규격 검수 및 자동 리사이징</p>
    </div>
    """, unsafe_allow_html=True)

# --- 2. GFA 5대 필수 규격 데이터 ---
AD_SPECS = {
    "스마트채널 (1250x370)": {"w": 1250, "h": 370},
    "네이버 메인 (1250x560)": {"w": 1250, "h": 560},
    "피드형 (1200x628)": {"w": 1200, "h": 628},
    "1:1 규격 (1200x1200)": {"w": 1200, "h": 1200},
    "배너형 (342x228)": {"w": 342, "h": 228}
}

# --- 3. 사이드바 설정 ---
st.sidebar.header("📂 규격 선택 및 업로드")
selected_ad = st.sidebar.selectbox("검수할 GFA 규격 선택", list(AD_SPECS.keys()))
spec = AD_SPECS[selected_ad]

uploaded_file = st.sidebar.file_uploader("검수할 이미지 파일을 불러오세요", type=['jpg', 'png', 'jpeg'])

st.sidebar.markdown("---")
st.sidebar.write(f"✅ **선택 규격:** {spec['w']} x {spec['h']} px")

# --- 4. 메인 검수 로직 ---
if uploaded_file:
    img = Image.open(uploaded_file)
    w, h = img.size
    
    st.subheader(f"📷 이미지 검수 리포트: {selected_ad}")
    
    col1, col2 = st.columns([2, 1])
    
    with col2:
        st.markdown("### 📝 검수 결과")
        if w == spec['w'] and h == spec['h']:
            st.success(f"✅ **규격 완벽 일치!**\n\n현재 이미지: {w}x{h}")
            final_img = img
            download_label = "📥 원본 이미지 다운로드 (JPG)"
        else:
            st.warning(f"⚠️ **규격 불일치**\n\n현재: {w}x{h} / 권장: {spec['w']}x{spec['h']}")
            final_img = img.resize((spec['w'], spec['h']), Image.Resampling.LANCZOS)
            download_label = "📥 리사이징 후 다운로드"

        buf = io.BytesIO()
        final_img.convert("RGB").save(buf, format="JPEG", quality=95)
        
        st.download_button(
            label=download_label,
            data=buf.getvalue(),
            file_name=f"GFA_READY_{selected_ad.split(' ')[0]}.jpg",
            mime="image/jpeg",
            use_container_width=True
        )

    with col1:
        st.image(final_img, use_container_width=True, caption=f"미리보기: {final_img.size[0]}x{final_img.size[1]}")

else:
    st.info("왼쪽 사이드바에서 이미지를 업로드하면 검수 및 최적화가 시작됩니다.")

# --- 5. 추가 가이드 (에러 발생 구간 수정) ---
st.markdown("---")
with st.expander("💡 GFA 광고 이미지 제작 팁"):
    st.write("""
    1. **파일 형식:** 네이버 GFA는 기본적으로 JPG 형식을 권장하며, RGB 색상 모드여야 합니다.
    2. **용량 제한:** 이미지당 500KB 이하로 제작하는 것이 가장 안정적입니다.
    3. **텍스트 비중:** 가급적 텍스트가 전체 면적의 20%를 넘지 않도록 배치하세요.
    """)
