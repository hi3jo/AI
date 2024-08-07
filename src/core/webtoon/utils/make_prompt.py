from dotenv import load_dotenv
from openai import OpenAI
import os

# OpenAI API 키 설정
client = OpenAI(
    api_key=os.getenv('OPENAI_API_KEY')
)

# 2024.07.10.수 : kyj 작성
def generate_prompt(i, sep_story, style):
    
    print("")
    print("--------------------------------------------------------------------------------------------------------------------------------------------------")
    print(f"make_prompt.py로 전달 된 사연 {i}번째 단락 \n\n 1)  내용 : {sep_story}")
    print("--------------------------------------------------------------------------------------------------------------------------------------------------")
    #gpt_model = "gpt-3.5-turbo"
    gpt_model = "gpt-4"
    
    # 1.ChatGPT를 사용하여 prompt 생성
    response = client.chat.completions.create(
          model=gpt_model
        , messages=[
             {"role": "system",    "content": "You are an assistant that creates detailed prompts for generating images."}
           , {"role": "user",      "content": sep_story}
           , {"role": "assistant", "content": style}
        ]
    )
    
    prompt = response.choices[0].message.content
    
    print()
    print(f"2) 영문 prompt 출력 : \n {prompt} \n\n")
    print("--------------------------------------------------------------------------------------------------------------------------------------------------")
    
    #trs_prpt = translate_ko(prompt)
    
    # 2.응답에서 사용된 토큰 수 정보 추출 (예시)
    #usage = response['usage']                                   
    #total_tokens = usage['total_tokens'] 
    #total_input_tokens = usage['prompt_tokens']
    #total_output_tokens = usage['completion_tokens']          
    #cost = calc_cost(total_input_tokens, total_output_tokens, gpt_model)
    
    #print(f"3) 총 사용된 토큰 수: {total_tokens}, 비용: ${cost:.4f} \n")
    #print("--------------------------------------------------------------------------------------------------------------------------------------------------")
    return prompt

# prompt에 따른 대략적인 비용 계산
def calc_cost(total_input_tokens, total_output_tokens, gpt_model):
    
    # 24.07.12.금요일 GPT를 통해 계산 로직 변경 함. 연구일지 확인 시 참고필요.
    # 모델별 토큰당 비용 (2024년 7월 기준 가정된 값, 실제 비용은 OpenAI 가격 페이지 확인)
    # 기준 : per 1K tokens
    token_costs = {
        "gpt-3.5-turbo": {"input": 0.0015 / 1000, "output": 0.002 / 1000}
        ,"davinci-002": {"input": 0.02 / 1000, "output": 0.02 / 1000}
        ,"davinci-003": {"input": 0.02 / 1000, "output": 0.02 / 1000}
        ,"curie-001": {"input": 0.002 / 1000, "output": 0.002 / 1000}
        ,"babbage-001": {"input": 0.0005 / 1000, "output": 0.0005 / 1000}
        ,"ada-001": {"input": 0.0004 / 1000, "output": 0.0004 / 1000}
        ,"gpt-4": {"input": 0.03 / 1000, "output": 0.06 / 1000}
    }
    
    input_cost  = total_input_tokens * token_costs[gpt_model]["input"]
    output_cost = total_output_tokens * token_costs[gpt_model]["output"]
    total_cost = input_cost + output_cost
    
    return total_cost

""" 
* GPT-3 시리즈
    - gpt-3.5-turbo: GPT-3.5 기반의 고성능 모델. 일반적인 대화 및 텍스트 생성 작업에 적합.
    - davinci-002, davinci-003: GPT-3의 고성능 버전으로, 복잡한 작업이나 창의적인 텍스트 생성에 적합.
    - curie-001: 다소 가벼운 모델로, 빠른 응답 시간과 적당한 성능을 제공.
    - babbage-001: 더 가벼운 모델로, 빠른 처리와 낮은 비용을 제공.
    - ada-001: 가장 가벼운 모델로, 가장 빠르고 저렴하지만 복잡한 작업에는 적합하지 않음.

* GPT-4 시리즈 (추후에 사용할 수 있는 경우)
    - gpt-4: 최신 및 최고 성능의 모델로, GPT-3 시리즈보다 뛰어난 성능을 제공. 복잡한 대화 및 텍스트 생성 작업에 적합. 
    
    token_costs = {
        "gpt-3.5-turbo": 0.0004     # 예시 비용 (달러 단위)
        ,"davinci-002": 0.02        
        ,"davinci-003": 0.02        
        ,"curie-001": 0.002         
        ,"babbage-001": 0.0005      
        ,"ada-001": 0.0004          
        ,"gpt-4": 0.03
    }
"""
