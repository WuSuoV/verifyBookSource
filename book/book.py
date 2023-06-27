import json
import os.path

from urllib3 import disable_warnings

disable_warnings()
from requests import get
from concurrent.futures import ThreadPoolExecutor


class book:
    def __init__(self, file):
        self.file = file
        self.type = self.recog_type(self.file)

    def recog_type(self, file: str):
        if file.startswith('http'):
            return 'url'
        elif os.path.exists(file):
            return os.path.splitext(file)[1]
        else:
            return None

    def json_to_books(self):
        if self.type == 'url':
            return get(url=self.file, verify=False).json()
        else:
            with open(self.file, mode='r', encoding='utf-8') as f:
                return json.loads(f.read())

    def check(self, abook, timeout=3):
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.58'
        }

        try:
            status = get(url=abook.get('bookSourceUrl'), verify=False,
                         headers=headers, timeout=timeout).status_code

            if status == 200:
                return {'book': abook, 'status': True}
            else:
                return {'book': abook, 'status': False}
        except Exception as e:
            return {'book': abook, 'status': False}

    def checkbooks(self, workers=16):
        pool = ThreadPoolExecutor(workers)
        books = self.json_to_books()
        ans = pool.map(self.check, books)
        good = []
        error = []

        # 代表当前检测了多少书源
        count = 0
        # 代表书源总数
        count_all = len(books)
        print('-'*16)
        print('检验进度：')
        for i in ans:
            if i.get('status'):
                good.append(i.get('book'))
            else:
                error.append(i.get('book'))
            # 设计进度条
            count = count + 1
            per = count/count_all

            p = '#' * int(per * 100 / 5)
            print(f'\r[{p}]', end='')
            print(f' \b{per:.2%}', end='')
        return {'good': good, 'error': error}

    def dedup(self, books: list):
        # 不重复书源的下标
        flag = []
        # 不重复书源的链接
        ans = []
        # 所有书源的链接
        urls = [i.get('bookSourceUrl') for i in books]

        for i in range(len(urls)):
            if urls[i] not in ans:
                ans.append(urls[i])
                flag.append(i)

        return [books[i] for i in flag]
