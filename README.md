# 꿀벌 디스펜서 모니터링 시스템

이 프로젝트는 꿀벌 디스펜서에서 나오는 꿀벌을 모니터링하는 연구의 일환으로 개발되었습니다. 디스펜서를 통해 나가는 꿀벌을 객체 탐지 모델로 탐지하여 꿀벌의 개수를 계산하고, 해당 데이터를 Flask를 통해 UI로 시각화합니다.

## 프로젝트 개요

이 시스템의 주요 목적은 꿀벌이 디스펜서를 떠나는 모습을 추적하고, 이를 통해 비벡터링 처리의 효과를 분석하는 것입니다. 객체 탐지 모델을 활용하여 디스펜서 출구에서 나가는 꿀벌을 실시간으로 감지하고, 이 데이터를 서버에서 처리하여 웹 기반 UI로 보여줍니다.

## 주요 기능

- **객체 탐지**: 오토인코더, 유넷, 어텐션 유넷 등의 모델을 이용해 꿀벌을 감지하고 개수를 계산합니다.
- **라즈베리파이 연동**: 라즈베리파이 카메라 모듈을 통해 실시간으로 꿀벌을 촬영합니다.
- **Google Drive API 연동**: 탐지된 데이터는 `.npy` 형식으로 저장되고, Google Drive에 업로드됩니다.
- **Flask 기반 UI**: Flask 서버가 데이터를 처리하고, 웹 UI에서 꿀벌의 출입 정보를 실시간으로 시각화합니다.
- **서버 측 데이터 처리**: 서버는 Google Drive API를 사용하여 `.npy` 파일을 가져와 분석하고, UI에 최신 데이터를 반영합니다.

## 기술 스택

- **하드웨어**: 라즈베리파이 (카메라 모듈 포함)
- **객체 탐지 모델**: 오토인코더, 유넷, 어텐션 유넷
- **백엔드**: Flask
- **클라우드 저장소**: Google Drive (Google Drive API 사용)
- **프론트엔드**: HTML/CSS (Flask 기반 UI)

## 설치 방법

1. 이 저장소를 클론합니다:
    ```bash
    git clone https://github.com/yourusername/bee-dispenser-monitoring.git
    cd bee-dispenser-monitoring
    ```

2. 필요한 Python 패키지를 설치합니다:
    ```bash
    pip install -r requirements.txt
    ```

3. Google Drive API 설정:
   - [이 가이드](https://developers.google.com/drive/api/v3/quickstart/python)를 참고하여 Google Drive API를 설정합니다.
   - `credentials.json` 파일을 프로젝트 디렉토리에 추가합니다.

4. 라즈베리파이 카메라 모듈을 연결하고, 설정을 완료합니다.

5. Flask 애플리케이션을 실행합니다:
    ```bash
    python app.py
    ```

6. 웹 브라우저에서 `http://localhost:5000`을 열어 애플리케이션에 접근할 수 있습니다.

## 프로젝트 구조

```
bee-dispenser-monitoring/ │
├── app.py # Flask 서버 및 UI 로직
├── detection/ # 객체 탐지 모델 코드
├── static/ # 정적 파일 (CSS, JavaScript, 이미지)
├── templates/ # HTML 템플릿
├── utils/ # 데이터 처리 유틸리티 함수
└── requirements.txt # 필요한 Python 패키지 목록
```

## 기여

이 연구는 지도교수님과의 협력으로 진행되었으며, 팀원들의 많은 기여와 지원이 있었습니다.
