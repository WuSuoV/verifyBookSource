import json
import os.path
import time

from book.book import book

if __name__ == '__main__':
    print("欢迎使用书源校验工具（VerifyBookSource v2.0）\n"
          "作者：勿埋我心 - SkyQian\n"
          "Github：https://github.com/Qiantigers/verifyBookSource\n"
          "我的博客：https://www.skyqian.com\n"
          f"{'-' * 16}")

    mode = input('是否使用config.json文件？（不使用则通过命令行输入配置）（y/n）')

    # 判断是否进入命令行输入配置
    if mode.lower() == 'n':
        path = input('本地文件路径/文件直链URL：')
        outpath = input('书源输出路径（为空则为当前目录，目录最后带斜杠）：')
        workers = input('请输入工作线程，填写数字（并不是越大越好）：')
        dedup = input('是否去重？（y/n）')
        with open('./config.json', mode='w', encoding='utf-8') as f:
            tmp = {
                'path': path,
                'workers': workers,
                'dedup': dedup,
                'outpath': outpath
            }
            json.dump(obj=tmp, fp=f, ensure_ascii=False, indent=4, sort_keys=False)

    # 判断配置文件是否存在
    if not os.path.exists('./config.json'):
        print('config.json文件不存在，请检查一下。或者使用命令行输入配置。')
    else:
        with open('./config.json', mode='r', encoding='utf-8') as f:
            config = json.load(f)

        books = book(config.get('path'))

        # 标记开始时间
        start_time = time.time()
        books_res = books.checkbooks(workers=int(config.get('workers')))

        good = books_res.get('good')
        error = books_res.get('error')

        if config.get('dedup') == 'y':
            good = books.dedup(good)

        with open(config.get('outpath') + 'good.json', 'w', encoding='utf-8') as f:
            json.dump(good, f, ensure_ascii=False, indent=4, sort_keys=False)

        with open(config.get('outpath') + 'error.json', 'w', encoding='utf-8') as f:
            json.dump(error, f, ensure_ascii=False, indent=4, sort_keys=False)

            s = len(books.json_to_books())
            g = len(good)
            e = len(error)
            print(f"\n{'-' * 16}\n"
                  "成果报表\n"
                  f"书源总数：{s}\n"
                  f"有效书源数：{g}\n"
                  f"无效书源数：{e}\n"
                  f"重复书源数：{(s - g - e) if config.get('dedup') == 'y' else '未选择去重'}\n"
                  f"耗时：{time.time() - start_time:.2f}秒\n")

    input('输入任意键退出……')
