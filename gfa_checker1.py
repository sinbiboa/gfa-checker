import streamlit as st
import easyocr
import numpy as np
from PIL import Image, ImageDraw
import io
import os

# --- 상단 디자인 커스텀 (배경 이미지 및 문구 적용) ---
st.markdown(f"""
    <style>
    /* 상단 헤더 부분 배경 설정 (GitHub에 올린 이미지 URL 사용) */
    [data-testid="stHeader"] {{
        background-image: url("https://raw.githubusercontent.com/YOUR_GITHUB_ID/gfa-checker/main/header_bg.jpg"); /* 본인 아이디로 수정 필수! */
        background-size: cover; /* 이미지가 꽉 차게 */
        background-position: center; /* 가운데 정렬 */
        background-repeat: no-repeat; /* 반복 없음 */
        height: 180px; /* 문구가 늘어나서 높이를 조금 더 줌 */
    }}
    
    /* 제목 부분 스타일 (배경 위에 잘 보이게 흰색 글자) */
    .main-title {{
        background-color: rgba(0, 0, 0, 0.6); /* 글자가 보이도록 반투명 검은색 배경 추가 */
        padding: 20px;
        border-radius: 10px;
        color: white; /* 흰색 글자 */
        text-align: center;
        margin-top: 30px; /* 제목 위치 조정 */
    }}
    
    /* 추가된 자신감 문구 스타일 */
    .confidence-text {{
        font-size: 24px; /* 글자 크기를 크게 */
        font-weight: bold; /* 굵게 */
        color: #FFD700; /* 금색(노란색)으로 포인트를 줌 */
        margin-top: 10px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5); /* 글자 뒤에 그림자 효과 */
    }}
    </style>
    <div class="main-title">
        <h1>🎯 GFA 광고 마스터 검수기</h1>
        <p>네이버 GFA 규격 및 텍스트 비중 자동 분석</p>
        <p class="confidence-text">야, 너도 GFA 할 수 있어!</p>
    </div>
    """, unsafe_allow_html=True)

# --- 페이지 설정 ---
st.set_page_config(page_title="GFA 마스터 검수기", layout="wide")
st.title("🛠️ GFA 광고 마스터 (자동 수정 & 가이드)")

# --- 광고 유형 설정 ---
AD_SPECS = {
    "스마트채널 (1250x370)": {"width": 1250, "height": 370, "size_limit": 500},
    "네이버 메인 (1250x560)": {"width": 1250, "height": 560, "size_limit": 500},
    "피드형 네이버/밴드 (1200x628)": {"width": 1200, "height": 628, "size_limit": 500},
    "피드형 1:1 규격 (1200x1200)": {"width": 1200, "height": 1200, "size_limit": 500}
}

@st.cache_resource
def load_ocr_model():
    return easyocr.Reader(['ko', 'en'], gpu=False)

reader = load_ocr_model()

# --- 사이드바 ---
st.sidebar.header("📋 설정")
selected_ad = st.sidebar.selectbox("광고 유형", list(AD_SPECS.keys()))
spec = AD_SPECS[selected_ad]
show_grid = st.sidebar.checkbox("5x5 오버레이 가이드 보기", value=True)

# --- 파일 업로드 ---
uploaded_file = st.file_uploader("이미지를 업로드하세요", type=['jpg', 'jpeg', 'png'])

if uploaded_file:
    raw_image = Image.open(uploaded_file)
    width, height = raw_image.size
    img_array = np.array(raw_image.convert('RGB'))
    
    # 1. AI 텍스트 분석
    with st.spinner('AI 분석 중...'):
        results = reader.readtext(img_array)

    # 2. 분석 가공용 이미지 복사
    processed_img = raw_image.copy()
    draw = ImageDraw.Draw(processed_img)
    
    text_boxes = []
    total_area = width * height
    current_text_area = 0

    for (bbox, text, prob) in results:
        x_coords = [p[0] for p in bbox]; y_coords = [p[1] for p in bbox]
        w = max(x_coords) - min(x_coords); h = max(y_coords) - min(y_coords)
        box_area = w * h
        current_text_area += box_area
        text_boxes.append({"text": text, "area": box_area, "bbox": bbox})
        draw.polygon([tuple(p) for p in bbox], outline="red", width=3)

    # 3. 오버레이 가이드 (그리드) 그리기
    if show_grid:
        for i in range(1, 5):
            # 세로선
            draw.line([(width/5*i, 0), (width/5*i, height)], fill="yellow", width=2)
            # 가로선
            draw.line([(0, height/5*i), (width, height/5*i)], fill="yellow", width=2)

    # --- 화면 구성 ---
    col1, col2 = st.columns([1.2, 1])

    with col1:
        st.subheader("📷 가이드 이미지")
        st.image(processed_img, use_container_width=True)
        st.caption("🔴 빨간박스: 텍스트 인식 영역 / 🟡 노란선: 5x5 그리드 가이드")

    with col2:
        st.subheader("📝 검수 및 시뮬레이션")
        text_ratio = (current_text_area / total_area) * 100
        
        # 메트릭
        st.write(f"**현재 상태:** {width}x{height} / {text_ratio:.1f}%")
        
        # 텍스트 삭제 시뮬레이션
        if text_ratio > 20:
            st.warning(f"⚠️ 텍스트 비중 초과! ({text_ratio:.1f}%)")
            st.write("**[삭제 제안]** 아래 문구들을 지우면 20% 이내가 됩니다:")
            
            # 넓이가 큰 순서대로 삭제 제안
            sorted_boxes = sorted(text_boxes, key=lambda x: x['area'], reverse=True)
            temp_area = current_text_area
            for box in sorted_boxes:
                if (temp_area / total_area) * 100 > 20:
                    st.write(f"- 🚩 `{box['text']}` (삭제 시 약 {box['area']/total_area*100:.1f}% 감소)")
                    temp_area -= box['area']
        else:
            st.success("✅ 텍스트 비중 통과!")

        st.markdown("---")
        st.subheader("💾 자동 수정 및 다운로드")
        
        # 자동 수정 로직
        if st.button("✨ 규격 자동 맞춤 & 최적화 실행"):
            # 1. 리사이징
            final_img = raw_image.resize((spec['width'], spec['height']), Image.Resampling.LANCZOS)
            
            # 2. 압축 및 바이트 변환
            buf = io.BytesIO()
            # 용량이 500KB 넘지 않을 때까지 화질 낮추며 반복 (최대 5번)
            quality = 95
            for i in range(5):
                buf = io.BytesIO()
                final_img.save(buf, format="JPEG", quality=quality)
                if len(buf.getvalue()) < spec['size_limit'] * 1024:
                    break
                quality -= 10
            
            st.download_button(
                label="📥 수정된 이미지 다운로드",
                data=buf.getvalue(),
                file_name=f"GFA_fixed_{selected_ad}.jpg",
                mime="image/jpeg"
            )
            st.info(f"결과: {spec['width']}x{spec['height']}로 리사이징 및 용량 최적화 완료!")