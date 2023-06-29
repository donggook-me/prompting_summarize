import crawler
import download
import prompt



def main():
    url = "https://chat.openai.com/share/6d4c906b-5a19-4c72-8ac0-899fcaf77a05"
    download.download_func(url)
    crawler.crawler()
    prompt.prompt_work("output_1.txt")

if __name__ == '__main__':
    main()