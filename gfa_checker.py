import streamlit as st
import easyocr
import numpy as np
from PIL import Image, ImageDraw
import io
import os

# --- 페이지 설정 ---
st.set_page_config(page_title="GFA 마스터 검수기", layout="wide")

# --- 상단 디자인 커스텀 (배경 이미지 및 문구 적용) ---
# YOUR_GITHUB_ID 부분을 본인 아이디로 수정하세요!
MY_ID = "sinbiboa" 
st.markdown(f"""
    <style>
    [data-testid="stHeader"] {{
        background-image: url("https://raw.githubusercontent.com/{MY_ID}/gfa-checker/main/header_bg.jpg");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        height: 180px;
    }}
    .main-title {{
        background-color: rgba(0, 0, 0, 0.6);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-top: 30px;
    }}
    .confidence-text {{
        font-size: 24px;
        font-weight: bold;
        color: #FFD700;
        margin-top: 10px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }}
    </style>
    <div class="main-title">
        <h1>🎯 GFA 광고 마스터 검수기</h1>
        <p>네이버 GFA 규격 및 텍스트 비중 자동 분석</p>
        <p class="confidence-text">야, 너도 GFA 할 수 있어!</p>
    </div>
    """, unsafe_allow_html=True)

# --- 광고 유형 설정 (배너형 추가) ---
AD_SPECS = {
    "스마트채널 (1250x370)": {"width": 1250, "height": 370, "size_limit": 500},
    "네이버 메인 (1250x560)": {"width": 1250, "height": 560, "size_limit": 500},
    "피드형 네이버/밴드 (1200x628)": {"width": 1200, "height": 628, "size_limit": 500},
    "피드형 1:1 규격 (1200x1200)": {"width": 1200, "height": 1200, "size_limit": 500},
    "배너형 (342x228)": {"width": 342, "height": 228, "size_limit": 500} # 👈 새로 추가!
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
    
    with st.spinner('AI 분석 중...'):
        results = reader.readtext(img_array)

    processed_img = raw_image.copy().convert('RGB') # 에러 방지를 위해 미리 RGB 변환
    draw = ImageDraw.Draw(processed_img)
    
    text_boxes = []
    total_area = width * height
    current_text_area = 0

    for (bbox, text, prob) in results:
        x_coords = [p[0] for p in bbox]; y_coords = [p[1] for p in bbox]
        w = max(x_coords) - min(x_coords); h = max(y_coords) - min(y_coords)
        box_area = w * h
        current_text_area += box_area
        text_boxes.append({"text": text, "area": box_area})
        draw.polygon([tuple(p) for p in bbox], outline="red", width=3)

    if show_grid:
        for i in range(1, 5):
            draw.line([(width/5*i, 0), (width/5*i, height)], fill="yellow", width=2)
            draw.line([(0, height/5*i), (width, height/5*i)], fill="yellow", width=2)

    col1, col2 = st.columns([1.2, 1])

    with col1:
        st.subheader("📷 가이드 이미지")
        st.image(processed_img, use_container_width=True)

    with col2:
        st.subheader("📝 검수 결과")
        text_ratio = (current_text_area / total_area) * 100
        st.write(f"**상태:** {width}x{height} / {text_ratio:.1f}%")
        
        if text_ratio > 20:
            st.warning(f"⚠️ 텍스트 과다! ({text_ratio:.1f}%)")
            sorted_boxes = sorted(text_boxes, key=lambda x: x['area'], reverse=True)
            temp_area = current_text_area
            for box in sorted_boxes:
                if (temp_area / total_area) * 100 > 20:
                    st.write(f"- 🚩 `{box['text']}` 지우기 제안")
                    temp_area -= box['area']
        else:
            st.success("✅ 통과!")

        st.markdown("---")
        st.subheader("💾 자동 수정 및 다운로드")
        
        if st.button("✨ 규격 자동 맞춤 & 최적화 실행"):
            # 1. 리사이징 시 배경 처리 (RGBA -> RGB 흰색 배경 처리)
            if raw_image.mode in ("RGBA", "P"):
                background = Image.new("RGB", raw_image.size, (255, 255, 255))
                background.paste(raw_image, mask=raw_image.split()[3])
                final_img = background
            else:
                final_img = raw_image.convert("RGB")
            
            final_img = final_img.resize((spec['width'], spec['height']), Image.Resampling.LANCZOS)
            
            # 2. 압축 및 저장 (에러 방지용 안전 로직 추가)
            quality = 95
            success = False
            for i in range(5):
                buf = io.BytesIO()
                try:
                    final_img.save(buf, format="JPEG", quality=quality)
                    if len(buf.getvalue()) < spec['size_limit'] * 1024:
                        success = True
                        break
                    quality -= 10
                except Exception as e:
                    st.error(f"저장 중 에러 발생: {e}")
                    break
            
            if success:
                st.download_button(
                    label="📥 수정된 이미지 다운로드",
                    data=buf.getvalue(),
                    file_name=f"GFA_fixed_{selected_ad}.jpg",
                    mime="image/jpeg"
                )
                st.info(f"{selected_ad} 규격({spec['width']}x{spec['height']}) 최적화 완료!")
