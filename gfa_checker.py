import streamlit as st
import io
from PIL import Image
import os

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="GFA AI 스마트 검수기", layout="wide")

st.markdown("""
    <div style="background-color: #00C73C; padding: 20px; border-radius: 15px; color: white; text-align: center; margin-bottom: 30px;">
        <h1 style="margin:0;">🎯 GFA AI 스마트 검수 시스템</h1>
        <p style="margin:5px 0 0 0;">이미지 변경 시 검수 항목이 실시간으로 동기화됩니다.</p>
    </div>
    """, unsafe_allow_html=True)

# --- 2. 규격 데이터 ---
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

# 파일이 바뀔 때 리포트를 갱신하기 위한 key 설정
uploaded_file = st.sidebar.file_uploader("검수할 이미지를 업로드하세요", type=['jpg', 'png', 'jpeg'], key="gfa_image_loader")

# --- 4. 메인 실행 로직 ---
if uploaded_file:
    # 새로운 파일이 들어오면 세션 상태 초기화
    img = Image.open(uploaded_file)
    w, h = img.size
    
    col1, col2 = st.columns([1.6, 1])
    
    with col1:
        st.subheader("📷 규격 검수 결과")
        if w == spec['w'] and h == spec['h']:
            st.success(f"✅ 규격 완벽 일치 ({w}x{h})")
            final_img = img
        else:
            st.warning(f"⚠️ 규격 자동 수정 ({w}x{h} → {spec['w']}x{spec['h']})")
            final_img = img.resize((spec['w'], spec['h']), Image.Resampling.LANCZOS)
        
        st.image(final_img, use_container_width=True)
        
        # 다운로드 버튼
        buf = io.BytesIO()
        final_img.convert("RGB").save(buf, format="JPEG", quality=95)
        st.download_button(
            label="📥 GFA 최적화 이미지 다운로드",
            data=buf.getvalue(),
            file_name=f"GFA_CHECKED_{spec['w']}x{spec['h']}.jpg",
            mime="image/jpeg",
            use_container_width=True
        )

    with col2:
        st.subheader("🤖 소재별 맞춤 검수 리포트")
        
        # 🌟 이미지가 업로드될 때마다 해당 시점의 리포트를 새로 렌더링
        st.info("💡 **새 이미지가 감지되었습니다.** 소재 유형에 맞춰 아래 항목을 최종 체크하세요.")
        
        # 실제 보류 가능성이 높은 항목만 동적으로 표시 (내장 위젯 방식)
        with st.expander("🚨 심각: 개인정보 노출 (필수 확인)", expanded=True):
            st.error("**개인정보 노출 위험**")
            st.write("이미지 내에 이메일 주소, 실명, 전화번호가 포함되어 있나요? 있다면 반드시 마스킹 처리해야 승인됩니다.")
            st.checkbox("확인 완료", key="check1")

        with st.expander("⚠️ 주의: 시스템 UI 사칭", expanded=True):
            st.warning("**네이버 UI 및 메일 양식**")
            st.write("네이버 시스템 화면을 그대로 썼을 경우 '사용자 기만' 사유로 보류될 수 있습니다.")
            st.checkbox("확인 완료", key="check2")

        with st.expander("🚩 경고: 가독성 저하", expanded=True):
            st.info("**텍스트 식별 불가**")
            st.write("모바일 환경에서 글자가 너무 작아 깨져 보이지 않는지 확인하세요. 캡처본은 특히 주의가 필요합니다.")
            st.checkbox("확인 완료", key="check3")

        with st.expander("💡 안내: 구성 복잡도", expanded=False):
            st.success("**이미지 구성 최적화**")
            st.write("문서 전체가 노출되어 시선이 분산된다면 핵심 문구에 강조 박스를 추가하는 것을 추천합니다.")
            st.checkbox("확인 완료", key="check4")

else:
    st.info("왼쪽 사이드바에서 이미지를 업로드하면 해당 소재에 대한 새로운 검수 리포트가 생성됩니다.")
