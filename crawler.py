import csv
from bs4 import BeautifulSoup




def crawler():
    with open("chat.html", "r", encoding="utf-8") as file:
        html_content = file.read()

    soup = BeautifulSoup(html_content, "html.parser")

    entries = soup.select(
        "#__next > div.overflow-hidden.w-full.h-full.relative.flex.z-0 > div > div > main > div.flex-1.overflow-hidden > div > div > div"
    )

    data = []
    for i in range(len(entries)):
        # 1 means human, 0 means ChatGPT
        entry = entries[i]
        is_human = i % 2 == 0

        # Check if the entry contains code
        code_element = entry.select_one(".p-4.overflow-y-auto code")
        code = code_element.text.strip() if code_element else ""

        # Extract the text, excluding the code if present
        text = entry.text.strip()
        if code:
            text = text.replace(code, "").strip()

        data.append((int(is_human), int(bool(code)), text, code))

    print("Chat data extracted successfully!")

    # Specify the filename for the CSV file
    csv_filename = "chat_data.csv"

    # Define the CSV headers
    headers = ["is_human", "has_code", "text", "code"]

    # Write the data to the CSV file
    with open(csv_filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        writer.writerows(data)

    print(f"Chat data saved to {csv_filename} successfully!")

if __name__ == '__main__':
    crawler()