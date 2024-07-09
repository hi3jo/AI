def seperater_contents(sentence):
    
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