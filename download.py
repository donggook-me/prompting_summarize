import requests



def download_func(url):
    TARGET_URL = url
    response = requests.get(TARGET_URL)
    html_content = response.text

    with open("chat.html", "w", encoding="utf-8") as file:
        file.write(html_content)

    print("HTML file downloaded successfully!")
    
if __name__ == '__main__':
    target_url = "https://chat.openai.com/share/f0009b3f-c126-4a6c-8163-1334b4cb7da6"
    download_func(target_url)
