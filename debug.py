import sys
import platform

print("=== 시스템 환경 진단 ===")
print(f"1. 파이썬 버전: {sys.version}")
print(f"2. 아키텍처: {platform.architecture()[0]}")
print("========================\n")

try:
    import mediapipe as mp
    print(f"3. MediaPipe 인식 경로: {mp.__file__}")
    
    print("4. 내부 엔진 강제 로드 시도 중...")
    # solutions를 거치지 않고 강제로 엔진 내부 깊숙한 곳을 찔러서 진짜 에러를 유발합니다.
    from mediapipe.python.solutions import holistic
    from mediapipe.python.solutions import drawing_utils
    print("✅ 5. 로드 성공! (이 메시지가 보인다면 일시적인 꼬임이 풀린 것입니다)")
    
except Exception as e:
    import traceback
    print("\n🚨 [숨겨진 진짜 에러가 나타났습니다!]")
    traceback.print_exc()
    