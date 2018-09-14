import requests
from bs4 import BeautifulSoup


def parse_url(page_url):
    headers = {
        'Host': 'maoyan.com',
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.92 Safari/537.36'
    }
    try:
        response = requests.get(page_url, headers=headers)
        soup = BeautifulSoup(response.text, 'lxml')
        data = soup.find_all('dd')
        for item in data:
            try:
                score = item.find("p", attrs={"class": "score"}).text.strip()
            except:
                print("it's not score for this film")
                score = "No Score"        # 龙猫没有分数, 单独处理
            yield {
                "rank": item.find("i").text,
                "name": item.find("p", attrs={"class": 'name'}).text.strip(),
                "star": item.find("p", attrs={"class": "star"}).text.strip(),
                "release_time": item.find("p", attrs={"class": "releasetime"}).text.strip(),
                "score": score
            }
    except Exception as e:
        print(e)
        return None


def save_to_txt(content):
    with open('maoyan_top100.txt', 'a', encoding='utf-8') as f:
        f.write(content["rank"] + '\t' + content['name'] + '\t' + content['star'] + '\t'
                + content['release_time'] + '\t' + content['score'] + '\n')


def main(page_url):
    for content in parse_url(page_url):
        save_to_txt(content)


if __name__ == "__main__":
    offset_list = [i*10 for i in range(0, 10)]
    for offset in offset_list:
        main('http://maoyan.com/board/4?offset={}'.format(offset))