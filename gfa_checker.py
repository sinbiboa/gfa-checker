import os
from openai import OpenAI

# 1. OpenAI 클라이언트 초기화
# 'api_key' 부분에 본인의 실제 API 키를 따옴표("") 안에 입력하세요.
# 보안을 위해 환경 변수를 사용하는 것이 좋지만, 여기서는 이해를 돕기 위해 직접 입력하는 방식을 사용합니다.
client = OpenAI(
    api_key="여기에_당신의_API_키를_넣으세요"
)

def generate_image_dalle3(prompt):
    """
    DALL-E 3를 사용하여 이미지를 생성하고 생성된 이미지의 URL을 반환합니다.
    """
    print(f"🎨 '{prompt}' 내용으로 이미지를 생성 중입니다. 잠시만 기다려 주세요...")

    try:
        # 2. DALL-E 3 API 호출
        response = client.images.generate(
            model="dall-e-3",            # 사용할 모델 (DALL-E 3 권장)
            prompt=prompt,               # 이미지를 설명하는 문장
            size="1024x1024",           # 이미지 크기 (1024x1024, 1024x1792, 1792x1024 가능)
            quality="standard",         # 화질 (standard 또는 hd)
            n=1                          # 생성할 이미지 개수 (DALL-E 3는 1개만 가능)
        )

        # 3. 생성된 이미지 URL 추출
        image_url = response.data[0].url
        print("✅ 이미지 생성 성공!")
        return image_url

    except Exception as e:
        print(f"❌ 오류가 발생했습니다: {e}")
        return None

# --- 메인 실행부 ---
if __name__ == "__main__":
    # 원하는 이미지의 내용을 한국어(또는 영어)로 상세하게 적어주세요.
    # 영어로 적을 때 더 정확한 결과가 나오는 경향이 있습니다.
    my_prompt = "A futuristic city built on floating islands in the sky, with waterfalls cascading down to the clouds, cinematic lighting, digital art style."

    # 함수 호출
    result_url = generate_image_dalle3(my_prompt)

    if result_url:
        print(f"\n🔗 생성된 이미지 확인하기 (이 링크를 클릭하세요):\n{result_url}")
        # 이 URL은 약 1시간 동안만 유효하므로 바로 접속해서 이미지를 저장해야 합니다.
