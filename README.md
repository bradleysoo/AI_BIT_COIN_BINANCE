# 🤖 AI Bitcoin Auto Trading Bot (Binance + Gemini API)

이 프로젝트는 **Google Gemini AI 모델**을 활용하여 비트코인 차트 데이터를 분석하고,  
매매 전략(`LONG`, `SHORT`, `HOLD`)을 결정하여 **바이낸스 선물 거래소에서 자동으로 트레이딩**을 수행합니다.



## 🧩 프로젝트 구조
```
ai_bit_coint_binace/
│
├── ai_analysis.py             # AI 분석 (Gemini)
├── autotrade.py               # 자동 거래 실행
├── get_char_from_binance.py   # Binance 차트 데이터 수집
├── .env                       # 환경변수 (API 키)
├── .gitignore                 # .env, __pycache__ 등 제외
├── requirements.txt           # 패키지 목록
└── README.md                  # 프로젝트 설명
```


## ⚙️ 주요 기능

### 1️⃣ get_char_from_binance.py
- **CCXT 라이브러리**를 통해 Binance Futures에서 `BTC/USDT`의 15분봉 데이터를 96개 조회 , 1시간봉 24개 조회
- `Pandas`로 가공하여 JSON 형태로 반환

### 2️⃣ ai_analysis.py
- **Google Generative AI (Gemini 2.5 Pro)** 모델을 사용
- 차트 데이터를 분석하여 다음 중 하나의 매매 전략을 결정:
  - `LONG`: 매수 포지션 진입  
  - `SHORT`: 매도 포지션 진입  
  - `HOLD`: 관망
- AI 판단 결과를 JSON 형태(`{"decision": "...", "reason": "..."}`)로 반환

### 3️⃣ autotrade.py
- **CCXT**를 사용해 Binance 선물 API와 연동
- AI의 판단 결과에 따라 자동으로 거래 수행
  - `LONG` → 시장가 매수 + 익절(+3%) / 손절(-3%) 주문 자동 설정  
  - `SHORT` → 시장가 매도 + 익절(-3%) / 손절(+3%) 주문 자동 설정
- 잔액 확인 및 미체결 주문 취소 로직 포함
- 주기적으로 시장 상황을 모니터링하며 자동 반복


## 🔐 환경 변수 (.env)

`.env` 파일은 **절대 깃허브에 업로드하지 마세요** ❗  
다음과 같은 형식으로 작성합니다:

## 🧰 설치 및 실행 방법

### 1️⃣ 필요한 라이브러리 설치
 `pip install -r requirements.txt` 한 줄이면 끝납니다


### 실행 예시 ##
```
 [12:30:12] Current BTC Price: $108,350.22
### AI Decision: LONG ###
### Reason: 상승 추세 강세 ###
```
