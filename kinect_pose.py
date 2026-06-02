import cv2
import mediapipe as mp
from pythonosc import udp_client

# ==========================================
# 1. 언리얼 엔진으로 데이터 보낼 주소 설정
# ==========================================
# 같은 PC에서 언리얼을 켠다면 "127.0.0.1"을 그대로 씁니다.
OSC_IP = "127.0.0.1" 
OSC_PORT = 8000
client = udp_client.SimpleUDPClient(OSC_IP, OSC_PORT)
print(f"[{OSC_IP}:{OSC_PORT}] 언리얼 엔진으로 OSC 전송 대기 중...")

# ==========================================
# 2. 미디어파이프(MediaPipe) 스켈레톤 설정
# ==========================================
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

# 키넥트 카메라 불러오기
# 숫자 0은 첫 번째 카메라를 의미합니다. 만약 화면이 안 뜬다면 1이나 2로 바꿔보세요!
cap = cv2.VideoCapture(1)

# 카메라 해상도 설정 (키넥트 V1 컬러 해상도 640x480)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# 포즈 인식 시작
with mp_pose.Pose(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5) as pose:
    
    print("카메라를 켭니다. 화면 창을 클릭하고 'q'를 누르면 종료됩니다.")
    
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("키넥트 화면을 불러올 수 없습니다. 카메라 번호를 확인하세요.")
            break

        # 미디어파이프 처리를 위해 색상 변환 (BGR -> RGB)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # 사람 뼈대 추출 (AI 연산)
        results = pose.process(image_rgb)

        # ==========================================
        # 3. 데이터 추출 및 언리얼 엔진(OSC) 전송
        # ==========================================
        if results.pose_landmarks:
            # 화면에 뼈대 그리기 (잘 인식되는지 눈으로 확인용)
            mp_drawing.draw_landmarks(
                image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
            
            # 33개의 관절 데이터를 언리얼로 발사!
            for idx, landmark in enumerate(results.pose_landmarks.landmark):
                osc_address = f"/pose/{idx}"
                # x, y, z 좌표를 리스트 형태로 전송
                client.send_message(osc_address, [landmark.x, landmark.y, landmark.z])

        # 좌우 반전(거울 모드)해서 화면에 보여주기
        cv2.imshow('Kinect + MediaPipe Pose', cv2.flip(image, 1))

        # 키보드 'q'를 누르면 창 닫기
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# 종료 시 카메라 자원 해제
cap.release()
cv2.destroyAllWindows()