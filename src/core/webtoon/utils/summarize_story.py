from transformers import PreTrainedTokenizerFast, BartForConditionalGeneration

# 1) EbanLee/kobart-summary-v3
def summarize_story(content):
    
    # Load Model and Tokenizer
    tokenizer = PreTrainedTokenizerFast.from_pretrained("EbanLee/kobart-summary-v3")
    model = BartForConditionalGeneration.from_pretrained("EbanLee/kobart-summary-v3")

    # Encoding
    input_text = content
    inputs = tokenizer(input_text, return_tensors="pt", padding="max_length", truncation=True, max_length=1026)

    # Generate Summary Text Ids
    # summary_text_ids = model.generate(
    # input_ids=inputs['input_ids'],
    # attention_mask=inputs['attention_mask'],
    # bos_token_id=model.config.bos_token_id,
    # eos_token_id=model.config.eos_token_id,
    # length_penalty=1.2,
    # max_length=280,
    # min_length=70,
    # num_beams=6,
    # repetition_penalty=1.5,
    # no_repeat_ngram_size=4,     #몇 단락으로 나눌지에 대한 기준(현재 4단락)
    # )
    
    summary_text_ids = model.generate(
    input_ids=inputs['input_ids'],
    attention_mask=inputs['attention_mask'],
    bos_token_id=model.config.bos_token_id,
    eos_token_id=model.config.eos_token_id,
    length_penalty=1.0,
    max_length=300,
    min_length=12,
    num_beams=6,
    repetition_penalty=1.5,
    no_repeat_ngram_size=15,
    )

    # Decoding Text Ids
    sum_text = tokenizer.decode(summary_text_ids[0], skip_special_tokens=True)
   
    print("")
    print("사연 요약 : ", sum_text)
    return sum_text


if __name__ == '__main__':
    
    content = ""
    summarize_story(content)