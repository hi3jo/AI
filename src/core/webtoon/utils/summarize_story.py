# 사연 요약하기
import openai
def summarize_story(story):
    try:
        
        prm = """Summarize the story into 4 paragraphs according to the following flow:
1. Initial problem
2. Escalation of conflict
3. Key incident
4. Conclusion and emotions"""
        # ChatGPT API 호출
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": prm},
                {"role": "user", "content": story}
            ],
            max_tokens=150,
            temperature=0.7,
            stop=["\n"]
        )

        # API 응답 처리
        if response['choices'] and len(response['choices']) > 0:
            summary = response['choices'][0]['message']['content']
        else:
            summary = "API에서 응답을 받지 못했습니다."

    except Exception as e:
        print(f"Error: {e}")
        summary = "API 호출 중 오류가 발생했습니다."

    return summary