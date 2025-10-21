import os

os.environ["GRPC_VERBOSITY"] = "NONE"  ##GCP 에러 메세지 막기
os.environ["GRPC_TRACE"] = ""
from dotenv import load_dotenv

load_dotenv()
import google.generativeai as genai
from get_char_from_binace import *
import json


def ai_analysis():

    # API 키 설정
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

    #  JSON 출력을 위한 모델 설정
    generation_config = {
        "response_mime_type": "application/json",
    }

    # 모델 초기화 (JSON 출력 설정을 포함)

    model = genai.GenerativeModel("gemini-2.5-pro", generation_config=generation_config)

    # 차트 데이터 가져오기
    data_payload_string = get_chart()

    # 프롬프트 구성
    prompt = f"""
  As a Bitcoin short-term investment expert, please advise which strategy to adopt—buy, sell, or hold—based on the provided chart data. Each investment must yield a 3–5% profit.
  Perform analysis based on the provided chart data:
  - 15-minute chart: 96 15-minute charts

  Respond in the following JSON format:
  {{“decision” : ‘long’, ‘reason’ : “technical reasons”}}
  {{“decision” : ‘short’, ‘reason’ : “technical reasons”}}
  {{“decision” : ‘hold’, ‘reason’ : “technical reasons”}}
  The chart data is as follows:
  {data_payload_string}

  """

    #  API 호출
    response = model.generate_content(prompt)

    #  결과 json 변형
    result_data = json.loads(response.text)

    # 결과(매수,매도,홀드)
    decision = result_data["decision"]
    # 이유
    reason = result_data["reason"]

    # ai 결과 출력
    print("### AI Decision: ", decision.upper(), "###")
    print("### Reason: ", reason, "###")
    return result_data

