import streamlit as st
import easyocr
import numpy as np
from PIL import Image, ImageDraw
import io
import os

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="GFA 마스터 검수기", layout="wide")

# --- 2. 상단 디자인 (이미지 없이 깔끔한 버전) ---
st.markdown("""
    <style>
    .main-header {
        background-color: #00C73C; 
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .confidence-text {
        font-size: 1.2rem;
        font-weight: bold;
        color: #FFD700;
        margin-top: 10px;
    }
    </style>
    <div class="main-header">
        <h1>🎯 GFA 광고 마스터 검수기</h1>
        <p>네이버 GFA 규격 및 텍스트 비중 자동 분석 도구</p>
        <p class="confidence-text">야, 너도 GFA 할 수 있어!</p>
    </div>
    """, unsafe_allow_html=True)

# --- 3. 광고 유형 설정 ---
AD_SPECS = {
    "스마트채널 (1250x370)": {"width": 1250, "height": 370, "size_limit": 500},
    "네이버 메인 (1250x560)": {"width": 1250, "height": 560, "size_limit": 500},
    "피드형 네이버/밴드 (1200x628)": {"width": 1200, "height": 628, "size_limit": 500},
    "피드형 1:1 규격 (1200x1200)": {"width": 1200, "height": 1200, "size_limit": 500},
    "배너형 (342x228)": {"width": 342, "height": 228, "size_limit": 500}
}

@st.cache_resource
def load_ocr_model():
    # 모델을 불러오는 동안 사용자가 기다릴 수 있게 캐싱합니다.
    return easyocr.Reader(['ko', 'en'], gpu=False)

reader = load_ocr_model()

# --- 4. 사이드바 설정 ---
st.sidebar.header("📋 설정")
selected_ad = st.sidebar.selectbox("광고 유형을 선택하세요", list(AD_SPECS.keys()))
spec = AD_SPECS[selected_ad]
show_grid = st.sidebar.checkbox("5x5 오버레이 가이드 보기", value=True)

# --- 5. 메인 기능: 파일 업로드 및 분석 ---
uploaded_file = st.file_uploader(f"[{selected_ad}] 이미지를 업로드하세요", type=['jpg', 'jpeg', 'png'])

if uploaded_file:
    raw_image = Image.open(uploaded_file)
    width, height = raw_image.size
    img_array = np.array(raw_image.convert('RGB'))
    
    with st.spinner('AI가 이미지를 정밀 분석 중입니다...'):
        results = reader.readtext(img_array)

    # 분석용 이미지 복사 (RGB 변환으로 에러 방지)
    processed_img = raw_image.copy().convert('RGB')
    draw = ImageDraw.Draw(processed_img)
    
    text_boxes = []
    total_area = width * height
    current_text_area = 0

    # OCR 결과 처리
    for (bbox, text, prob) in results:
        x_coords = [p[0] for p in bbox]
        y_coords = [p[1] for p in bbox]
        w = max(x_coords) - min(x_coords)
        h = max(y_coords) - min(y_coords)
        
        box_area = w * h
        current_text_area += box_area
        text_boxes.append({"text": text, "area": box_area})
        
        # 빨간 박스 그리기
        draw.polygon([tuple(p) for p in bbox], outline="red", width=3)

    # 5x5 그리드 그리기
    if show_grid:
        for i in range(1, 5):
            draw.line([(width/5*i, 0), (width/5*i, height)], fill="yellow", width=2)
            draw.line([(0, height/5*i), (width, height/5*i)], fill="yellow", width=2)

    # 화면 분할 출력
    col1, col2 = st.columns([1.2, 1])

    with col1:
        st.subheader("📷 분석 가이드 이미지")
        st.image(processed_img, use_container_width=True)

    with col2:
        st.subheader("📝 검수 결과 리포트")
        text_ratio = (current_text_area / total_area) * 100
        st.write(f"**현재 해상도:** {width}x{height}")
        st.write(f"**텍스트 비중:** {text_ratio:.1f}%")
        
        if text_ratio > 20:
            st.warning("⚠️ 텍스트 비중이 20%를 초과했습니다.")
            st.write("**[삭제 추천 리스트]** (면적이 큰 순서)")
            sorted_boxes = sorted(text_boxes, key=lambda x: x['area'], reverse=True)
            temp_area = current_text_area
            for box in sorted_boxes:
                if (temp_area / total_area) * 100 > 20:
                    st.write(f"- `{box['text']}`")
                    temp_area -= box['area']
        else:
            st.success("✅ GFA 텍스트 비중 규격을 통과했습니다!")

        st.markdown("---")
        st.subheader("💾 자동 규격 최적화")
        
        if st.button("✨ 클릭하여 규격 맞춤 및 용량 압축"):
            # PNG 투명도 처리 (흰색 배경 합성)
            if raw_image.mode in ("RGBA", "P"):
                background = Image.new("RGB", raw_image.size, (255, 255, 255))
                background.paste(raw_image, mask=raw_image.split()[3])
                final_img = background
            else:
                final_img = raw_image.convert("RGB")
            
            # 해상도 리사이징
            final_img = final_img.resize((spec['width'], spec['height']), Image.Resampling.LANCZOS)
            
            # 파일 용량 최적화 (500KB 제한)
            quality = 95
            success = False
            for _ in range(5):
                buf = io.BytesIO()
                final_img.save(buf, format="JPEG", quality=quality)
                if len(buf.getvalue()) < spec['size_limit'] * 1024:
                    success = True
                    break
                quality -= 10
            
            if success:
                st.download_button(
                    label="📥 최적화 완료 이미지 다운로드",
                    data=buf.getvalue(),
                    file_name=f"GFA_fixed_{selected_ad}.jpg",
                    mime="image/jpeg"
                )
                st.info(f"변환 완료: {spec['width']}x{spec['height']}")
