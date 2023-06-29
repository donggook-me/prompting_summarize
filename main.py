import crawler
import download
import prompt



def main():
    url = "https://chat.openai.com/share/6fbd84db-4cb0-4467-8c66-79b94e2d8666"
    download.download_func(url)
    crawler.crawler()
    prompt.prompt_work("output_1.txt")

if __name__ == '__main__':
    main()