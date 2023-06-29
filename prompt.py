import openai
import os
import csv
import tiktoken
from dotenv import load_dotenv

# load .env
load_dotenv()

class prompt_work():
    
    openai.api_key = os.environ.get('OPENAI_API_KEY_SERVICE')
    
    # 클래스 시작 함수
    def __init__(self, output_filename) -> None:
        self.filename = output_filename
        self.max_tokens = 16000
        self.split_size = 1
        self.prompt = ""
        self.result = self.run_all()

    def get_resp_text(self):
        return self.result
    # GPT 에 요청 함수
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
    
    def compressPrompt(self,prompt, prompt_tokens):
        print(f"token count is....{prompt_tokens}")
        
        if prompt_tokens > (self.max_tokens/2):
            # 16K 의 절반 -> 8K 보다 프롬팅이 클시 전처리 요구됨.
            self.split_size = int(prompt_tokens // (self.max_tokens/2)) + 1
            print(f"split size is {self.split_size}")
            split_prompts = []
            for i in range(0, self.split_size):
                split_prompts.append([prompt[int(i * (self.max_tokens // 2)) : int((i + 1) * (self.max_tokens // 2))]])

            merged_data = ""
            for prom in split_prompts:
                merged_data += self.summarize_each_piece(prom)
            print("merged_data : ", merged_data + "\n")
            return merged_data
        else:
            # 8K 보다 작을시 문제 없음. 
            return prompt
    
    def summarize_each_piece(self, parsed_prompt) -> str:
        summarizing_prompt = f"""
        Hello, you are now my assistant summarizing this content. 
        This conversational data is the content of questions that arose during coding or how to modify the code.
        Among them, analyze the words and ask them to write a code, 
        or summarize them around the part where you ask them to revise the code.
        Please make this summarize into {self.max_tokens/2/self.split_size} tokens count.
        ```{parsed_prompt}```
        """
        response = self.get_completion(summarizing_prompt)
        return response
        
    # 요약하는 프로그래밍-조수 역할 부여하여 GPT 에 요청하는 함수.
    def summarize_func(self, ver_name, filename):
        
        # 토큰 개수가 8000 을 넘을시, 여러개의 조각으로 나눠서 각각 요약한 뒤 다시 합쳐서 요청.
        tokens_count = self.num_tokens_from_string(self.prompt, "cl100k_base")
        processed_data = self.compressPrompt(self.prompt, tokens_count)
        
        self.prompt = f"""
                
        Hi, You are programming-assistant. I'll give conversation history with you. I hope you summarize it into at least 3 dotted text in korean. Can you do this Following STEP?

        If there are irregular sequential data or expression, just skip it. 

        STEP1. You'll get each text data, that includes my question "how to make this function? or why this doesn't work?" and sequentially your answer about how to write in.

        STEP2. Summarize about codes that I've asked you to make. do not include the other sentence in summarizing Just include each thing you made for me.

        STEP3. Translate it in Korean. 

        STEP4. Change Korean sentence into this Format "-- 어떤 요청을 받아 -- 기능의 구현을 도움받음."
        
        execute this step with beflow data. This data is preSummarized data(focused on prompt user asked for gpt to make or write or fix code)
        
        ```{processed_data}```
        """
        
        response = self.get_completion(self.prompt)

        # Check if the file already exists
        if os.path.exists(filename):
            # File already exists, open it in append mode
            with open(filename, "a", encoding="utf-8") as file:
                file.write("--------------" + "\n")
                file.write(ver_name)
                file.write(response + "\n")
        else:
            # File doesn't exist, create a new file and write to it
            with open(filename, "w", encoding="utf-8") as file:
                file.write("--------------" + "\n")
                file.write(ver_name + "\n")
                file.write(response + "\n")

        print(f"{ver_name} Summary saved to {filename} successfully!")
        return response
    
    
    # 전체 실행 함수
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
        response_txt = self.summarize_func("human_and_gpt_without_code", self.filename)
        return response_txt

if __name__ == '__main__':
    output_filename = "output_2.txt"
    pw = prompt_work(output_filename)
    print(pw)
