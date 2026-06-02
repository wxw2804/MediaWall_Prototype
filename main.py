import cv2
import mediapipe as mp
from pythonosc import udp_client

def main():
    # 1. OSC 통신 클라이언트 설정
    # 데이터를 받을 목적지(내 PC의 언리얼 엔진)의 IP와 포트 번호를 설정합니다.
    osc_ip = "127.0.0.1" # 로컬 호스트 (내 PC)
    osc_port = 8000      # 언리얼 엔진에서 수신할 포트 번호
    client = udp_client.SimpleUDPClient(osc_ip, osc_port)
    print(f"OSC 연결 준비 완료 -> 목적지: {osc_ip}:{osc_port}")

    # 2. MediaPipe 초기 설정 (전신 및 손 추적)
    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles
    mp_holistic = mp.solutions.holistic

    # 3. 카메라 설정 (기존에 성공한 4번 인덱스 적용)
    cap = cv2.VideoCapture(4, cv2.CAP_DSHOW)

    if not cap.isOpened():
        print("카메라를 열 수 없습니다. 스마트폰 연동 앱을 확인하세요.")
        return

    print("MediaPipe & OSC 실시간 전송 시작! (종료하려면 화면 클릭 후 'q' 입력)")

    # Holistic 모델 로드
    with mp_holistic.Holistic(
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5) as holistic:

        while True:
            ret, frame = cap.read()
          
            if not ret:
                break

            # 직관적인 거울 모드 적용
            frame = cv2.flip(frame, 1)

            # 이미지 색상 변환 및 최적화
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_rgb.flags.writeable = False
            
            # 모델 분석 (좌표 추출)
            results = holistic.process(frame_rgb)
            
            frame_rgb.flags.writeable = True
            frame = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)

            # ----------------------------------------------------
            # 4. 핵심: 좌표 추출 및 OSC 전송 로직
            # ----------------------------------------------------
            # MediaPipe에서 8번 랜드마크는 '검지손가락 끝(Index Finger Tip)'입니다.
            # 추출되는 X, Y 좌표는 0.0 ~ 1.0 사이의 비율(비례) 값입니다.
            
           # ----------------------------------------------------
            # 4. 핵심: 전신(Pose) 좌표 추출 및 OSC 전송 로직
            # ----------------------------------------------------
            if results.pose_landmarks:
                pose_data = []
                
                # Holistic 모델이 제공하는 33개 관절 전체를 순회합니다.
                for landmark in results.pose_landmarks.landmark:
                    # 언리얼에서 계산하기 편하도록 x, y, z를 순서대로 리스트에 추가
                    # MediaPipe의 Y축은 위가 0이므로, 언리얼과 맞추기 위해 그대로 보낸 뒤 엔진에서 보정합니다.
                    pose_data.append(float(landmark.x))
                    pose_data.append(float(landmark.y))
                    pose_data.append(float(landmark.z)) # 깊이 값 포함
                
                # "/pose/all"이라는 하나의 주소로 99개(33개 관절 * 3개 좌표)의 데이터를 쏩니다.
                client.send_message("/pose/all", pose_data)
            # ----------------------------------------------------

            # 5. 화면에 뼈대 그리기 (정상 작동 확인용 시각화)
            if results.right_hand_landmarks:
                mp_drawing.draw_landmarks(frame, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS, mp_drawing_styles.get_default_hand_landmarks_style(), mp_drawing_styles.get_default_hand_connections_style())
            if results.left_hand_landmarks:
                mp_drawing.draw_landmarks(frame, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS, mp_drawing_styles.get_default_hand_landmarks_style(), mp_drawing_styles.get_default_hand_connections_style())
            if results.pose_landmarks:
                mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS, landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())

            cv2.imshow('MediaWall - OSC Transmitter', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()