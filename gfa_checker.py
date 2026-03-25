import streamlit as st
import easyocr
import numpy as np
from PIL import Image, ImageDraw
import io
import os
import requests # 이미지 생성을 위한 라이브러리 추가

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="GFA 마스터 PRO", layout="wide")

# --- 2. 상단 디자인 (깔끔한 버전) ---
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
    /* 사이드바 스타일 정의 */
    [data-testid="stSidebar"] {
        background-color: #f0f2f6;
    }
    </style>
    <div class="main-header">
        <h1>🎯 GFA 광고 마스터 PRO</h1>
        <p>AI 이미지 생성 및 규격/텍스트 자동 분석 도구</p>
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

# --- 4. 사이드바 메뉴 (제미나이 스타일처럼 메뉴 분리) ---
st.sidebar.markdown("# 🛠️ 메뉴 선택")

# 메인 메뉴 선택 (검수 vs 생성)
menu_option = st.sidebar.radio(
    "원하시는 작업을 선택하세요",
    ("🔍 GFA 광고 규격 검수", "🎨 AI 광고 이미지 생성(베타)"),
    label_visibility="collapsed"
)

st.sidebar.markdown("---")

# ==========================================
# 🔍 1. GFA 광고 규격 검수 기능
# ==========================================
if menu_option == "🔍 GFA 광고 규격 검수":
    st.header("🔍 GFA 광고 규격 및 텍스트 비중 검수")
    
    # OCR 모델 로딩 (검수 메뉴에서만 로딩)
    @st.cache_resource
    def load_ocr_model():
        return easyocr.Reader(['ko', 'en'], gpu=False)

    reader = load_ocr_model()

    # 사이드바 설정 (검수용)
    st.sidebar.header("📋 검수 설정")
    selected_ad = st.sidebar.selectbox("검수할 광고 유형", list(AD_SPECS.keys()))
    spec = AD_SPECS[selected_ad]
    show_grid = st.sidebar.checkbox("5x5 오버레이 가이드 보기", value=True)

    # 메인 기능: 파일 업로드 및 분석
    uploaded_file = st.file_uploader(f"[{selected_ad}] 이미지를 업로드하세요", type=['jpg', 'jpeg', 'png'])

    if uploaded_file:
        raw_image = Image.open(uploaded_file)
        width, height = raw_image.size
        img_array = np.array(raw_image.convert('RGB'))
        
        with st.spinner('AI가 이미지를 정밀 분석 중입니다...'):
            results = reader.readtext(img_array)

        processed_img = raw_image.copy().convert('RGB')
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
            st.subheader("📷 분석 가이드 이미지")
            st.image(processed_img, use_container_width=True)

        with col2:
            st.subheader("📝 검수 결과 리포트")
            text_ratio = (current_text_area / total_area) * 100
            st.write(f"**현재 해상도:** {width}x{height} / **텍스트 비중:** {text_ratio:.1f}%")
            
            if text_ratio > 20:
                st.warning("⚠️ 텍스트 비중 20% 초과! 삭제 추천 리스트:")
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
                if raw_image.mode in ("RGBA", "P"):
                    background = Image.new("RGB", raw_image.size, (255, 255, 255))
                    background.paste(raw_image, mask=raw_image.split()[3])
                    final_img = background
                else:
                    final_img = raw_image.convert("RGB")
                
                final_img = final_img.resize((spec['width'], spec['height']), Image.Resampling.LANCZOS)
                
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

# ==========================================
# 🎨 2. AI 광고 이미지 생성 기능(베타)
# ==========================================
elif menu_option == "🎨 AI 광고 이미지 생성(베타)":
    st.header("🎨 AI GFA 광고 이미지 생성(베타)")
    st.write("원하시는 광고 이미지를 텍스트로 설명해 주세요. (맛보기용 무료 모델 사용)")

    # 사이드바 설정 (생성용)
    st.sidebar.header("📋 생성 설정")
    gen_ad_type = st.sidebar.selectbox("생성할 광고 규격", list(AD_SPECS.keys()))
    gen_spec = AD_SPECS[gen_ad_type]

    # 프롬프트 입력
    prompt = st.text_area(
        "이미지 설명 (프롬프트)", 
        "여름 시즌 세일 배너, 시원한 바다 배경, 코코넛 음료, 밝은 분위기, 'SUMMER SALE' 글자 배제",
        height=100,
        help="GFA는 텍스트 비중이 중요하므로, 글자는 디자인 툴로 직접 넣는 것을 추천합니다. 글자는 배제하고 디자인 배경 위주로 설명해 주세요."
    )

    # 프롬프트를 영어로 번역하는 기능 (무료 모델은 영어를 훨씬 잘 알아듣습니다)
    translate_option = st.sidebar.checkbox("입력한 프롬프트를 AI가 자동 번역(권장)", value=True)

    if st.button("✨ 광고 이미지 생성 실행"):
        if not prompt:
            st.error("이미지 설명을 입력해 주세요.")
        else:
            with st.spinner('AI가 광고 이미지를 생성하고 있습니다... (약 1분 소요)'):
                
                # 1. 프롬프트 처리
                final_prompt = prompt
                if translate_option:
                    try:
                        # 맛보기용 무료 번역 API (구글 번역 기반)
                        trans_url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=ko&tl=en&dt=t&q={prompt}"
                        trans_res = requests.get(trans_url).json()
                        final_prompt = trans_res[0][0][0]
                        st.info(f"🌐 번역된 프롬프트: {final_prompt}")
                    except:
                        st.warning("프롬프트 번역에 실패했습니다. 한국어 프롬프트 그대로 사용합니다.")

                # 2. 이미지 생성 API 호출 (Pollinations.ai - 무료/무제한 사용)
                # 이 모델은 빠르고 무료지만, 퀄리티가 고사양 AI에 비해 낮을 수 있습니다.
                # GFA 규격으로 자동 리사이징하여 가져옵니다.
                gen_url = f"https://image.pollinations.ai/prompt/{final_prompt}?width={gen_spec['width']}&height={gen_spec['height']}&nologo=true&seed=42"
                
                try:
                    gen_res = requests.get(gen_url)
                    if gen_res.status_code == 200:
                        gen_image = Image.open(io.BytesIO(gen_res.content))
                        
                        st.subheader("📷 생성된 광고 이미지 배경")
                        st.image(gen_image, use_container_width=True)
                        st.caption(f"규격: {gen_spec['width']}x{gen_spec['height']} (프롬프트: {final_prompt})")

                        # 3. 다운로드 버튼
                        buf = io.BytesIO()
                        gen_image.save(buf, format="PNG")
                        st.download_button(
                            label="📥 생성된 이미지 다운로드",
                            data=buf.getvalue(),
                            file_name=f"GFA_gen_{gen_ad_type}.png",
                            mime="image/png"
                        )
                        st.success("이미지가 생성되었습니다! 다운로드 후 텍스트를 추가하여 완성하세요.")
                    else:
                        st.error("이미지 생성 서버에 연결할 수 없습니다. 잠시 후 다시 시도해 주세요.")
                except Exception as e:
                    st.error(f"이미지 생성 중 오류 발생: {e}")

    st.markdown("---")
    st.info("💡 **GFA 제작 팁:** AI는 글자를 정확하게 그리지 못합니다. 여기서는 디자인 배경만 생성하고, 포토샵이나 피그마 같은 디자인 툴로 글자를 직접 얹어야 GFA 심사를 통과할 수 있습니다.")
