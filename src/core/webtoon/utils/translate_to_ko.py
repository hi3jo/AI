""" from googletrans import Translator

def translate_ko(prompt):
    
    # 번역할 문장 입력
    text = prompt
    
    # 번역 객체 생성
    translator = Translator()

    # 번역 실행
    result = translator.translate(text, dest='ko')

    # 번역 결과 출력
    #print(result.text)
    return result """
