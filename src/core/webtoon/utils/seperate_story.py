def separate_contents(sentence):
    
    # 텍스트를 무조건 4단락으로 나누기
    num_prompts = 4
    sentence_length = len(sentence)
    chars_per_prompt = sentence_length // num_prompts
    prompts = []

    for i in range(num_prompts):
        start_idx = i * chars_per_prompt
        if i == num_prompts - 1:
            end_idx = sentence_length  # 마지막 단락은 끝까지
        else:
            end_idx = (i + 1) * chars_per_prompt
        prompt = sentence[start_idx:end_idx].strip()
        prompts.append(prompt)

    return prompts

def separate_contents_spacebar(sentence, num_newlines=15):
    # 입력 문장을 개행 문자('\n\n') 15개가 나올 때마다 자르기
    prompts = []
    current_prompt = ""

    for char in sentence:
        current_prompt += char
        
        # 개행 문자('\n\n') 15개가 나오면 현재 prompt를 리스트에 추가하고 초기화
        if char == '\n' and len(current_prompt.split('\n\n')) == num_newlines:
            prompts.append(current_prompt.strip())
            current_prompt = ""

    # 마지막 남은 부분 추가
    if current_prompt:
        prompts.append(current_prompt.strip())

    return prompts