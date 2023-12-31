import openai
import os
import csv
import tiktoken
import concurrent.futures
import threading


class prompt_work():
    def __init__(self, output_filename) -> None:
        self.filename = output_filename
        self.max_tokens = 16000
        self.split_size = 1
        self.prompt = ""
        self.result = self.run_all()
    
    # class init return function
    def get_resp_text(self):
        return self.result.replace("\n", " ")
    
    # GPT Chat api call func
    def get_completion(self, prompt, model="gpt-3.5-turbo-16k"):
        messages = [{"role": "user", "content": prompt}]
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=0,  # this is the degree of randomness of the model's output
        )
        return response.choices[0].message["content"]

    # Load only humans' text (excluding GPT's answers)
    def load_human_text(self, csv_filename):
        with open(csv_filename, "r", encoding="utf-8") as file:
            reader = csv.reader(file)
            next(reader)  # Skip header row
            text = ""
            for row in reader:
                is_human, _, entry_text, _ = row
                if is_human == "True":
                    text += entry_text + " "
            return text.strip()

    # Load humans' and GPT's answers together (including the "code" column)
    def load_chat_data(self, csv_filename):
        with open(csv_filename, "r", encoding="utf-8") as file:
            reader = csv.reader(file)
            next(reader)  # Skip header row
            text = ""
            for row in reader:
                _, _, entry_text, code = row
                text += entry_text + " " + code + " "
            return text.strip()

    # Load humans' and GPT's answers without the code part
    def load_text_without_code(self, csv_filename):
        with open(csv_filename, "r", encoding="utf-8") as file:
            reader = csv.reader(file)
            next(reader)  # Skip header row
            text = ""
            for row in reader:
                _, _, entry_text, code = row
                text += entry_text.replace(code, "") + " "
            return text.strip()
        
        
    def num_tokens_from_string(self,string: str, encoding_name: str) -> int:
        """Returns the number of tokens in a text string."""
        encoding = tiktoken.get_encoding(encoding_name)
        num_tokens = len(encoding.encode(string))
        return num_tokens    

    def compressPrompt(self, prompt, prompt_tokens):
        print(f"token count is....{prompt_tokens}")
        
        if prompt_tokens > (self.max_tokens/2):
            # half of 16K, because 8K is on Question, rest of 8K is used on Answering.
            self.split_size = int(prompt_tokens // (self.max_tokens/2)) + 1
            print(f"split size is {self.split_size}")
            split_prompts = []
            for index, i in enumerate(range(0, self.split_size)):
                start_idx = (int(len(prompt) / self.split_size) * i)
                end_idx = (int(len(prompt) / self.split_size) * (i+1) ) - 1
                split_prompts.append([prompt[start_idx : end_idx]])
                print(f"{index} segment range is ({start_idx},{end_idx})")

            # running each splitted text dummy summarizing in multi-threading.
            merged_data = ""
            lock = threading.Lock()

            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = []
                for prom in split_prompts:
                    future = executor.submit(self.summarize_each_piece, prom)
                    futures.append(future)

                for future in concurrent.futures.as_completed(futures):
                    result = future.result()
                    with lock:
                        merged_data += result

            print("merged_data : ", merged_data + "\n")
            return merged_data
        else:
            # if it's smaller than 8K, just go Straight.
            return prompt

    # it is used when text prompt is bigger than 8K.
    def summarize_each_piece(self, parsed_prompt) -> str:
        summarizing_prompt = f"""
        Hello, you are now my assistant summarizing this content. 
        This conversational data is the content of questions that arose during coding or how to modify the code.
        Among the contents of the conversation, focus on the parts that requested code writing or modification, bug fixing, etc.
        Please make this sentences summarized into short version sentenced in {self.max_tokens/2/self.split_size} tokens count.
        ```{parsed_prompt}```
        """
        response = self.get_completion(summarizing_prompt)
        print("토큰 사이즈 초과로, 분할하여 요약 중..." + "\n") 
        return response

        
    # Asking GPT to act like programming-summarizing assistant.
    def summarize_func(self, start_sentence, filename):
        
        # if token count is bigger than 8K, go to the func, split and merge into smaller set.
        tokens_count = self.num_tokens_from_string(self.prompt, "cl100k_base")
        processed_data = self.compressPrompt(self.prompt, tokens_count)
        
        self.prompt = f"""
                
        Hi, You are programming-assistant. I'll give conversation history with you. I hope you summarize it into at least 3 dotted text in korean. Can you do this Following STEP?

        If there are irregular sequential data or expression, just skip it. 
        
        And Also, If you have any previous data, just erase it. And focus on the data I'll give you.

        STEP1. You'll get each text data, that includes my question "how to make this function? or why this doesn't work?" and sequentially your answer about how to write in.

        STEP2. Summarize about codes that I've asked you to make. do not include the other sentence in summarizing Just include each thing you made for me.

        STEP3. Translate it in Korean. 

        STEP4. Change Korean sentence into one of this Format "XXX 개념을 질문함.", "XXX 기능의 구현을 도움받음.", "XXX 기능의 코드 수정을 도움받음", "XXX 에러 발생의 수정을 도움받음",
        You'll replace XXX with what you've extracted. And Please end each line with this style of word "받음" or "했음".
        
        STEP5. Write only one sentence on each line. Do not make over 5 lines.
        
        execute this step with beflow data. This data is preSummarized data(focused on prompt user asked for gpt to make or write or fix code)
        
        ```{processed_data}```
        """
        
        response = self.get_completion(self.prompt)

        # open new file and write response to it.
        with open(filename, "w", encoding="utf-8") as file:
            file.write(start_sentence)
            file.write(response)

        print(f"{start_sentence} Summary saved to {filename} successfully!")
        return response
    
    
    # main running func.
    def run_all(self):
        csv_filename = "chat_data.csv"

        # # user data
        # result_text = self.load_human_text(csv_filename)
        # test_text = f"""{result_text}"""
        # self.summarize_func(test_text, "human_text", self.filename)

        # # user + gpt data with code
        # result_text = self.load_chat_data(csv_filename)
        # test_text = f"""{result_text}"""
        # self.summarize_func(test_text, "human_and_gpt_with_code", self.filename)

        # user + gpt data without code
        result_text = self.load_text_without_code(csv_filename)
        self.prompt = f"""{result_text}"""
        response_txt = self.summarize_func("ChatGPT와의 질의응답을 통해 다음을 참고하였습니다.", self.filename)
        return response_txt

if __name__ == '__main__':
    output_filename = "output_2.txt"
    pw = prompt_work(output_filename)
    print(pw)
