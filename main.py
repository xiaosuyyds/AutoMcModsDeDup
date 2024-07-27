import argparse
import os
import re
import shutil

import requests
from tqdm import tqdm
import time
import random
from bs4 import BeautifulSoup

mod_name_del_key_list = [
    {
        "type": "regex",
        "pattern": r"\b([Vv])?([Mm][Cc])?\d+(?:\.\d+){0,2}(?:\.x)?\b",
    },
    {"type": "regex", "pattern": r"\b[Bb]uild\.?\d+\b"},
    {"type": "regex", "pattern": r"\b[a-fA-F0-9]{6,7}\b"},
    {"type": "regex", "pattern": r"(?i)\b(?:alpha|beta)(?:\.\d{1,3}){0,3}\b"},
    {"type": "string", "pattern": "mc"},
    {"type": "string", "pattern": "mod"},
    {"type": "string", "pattern": "forge"},
    {"type": "string", "pattern": "fabric"},
    {"type": "string", "pattern": "f"},
]


def get_mod_file_list(path):
    mod_file_list = []
    for file in os.listdir(path):
        if file.endswith(".jar"):
            mod_file_list.append(file)
    return mod_file_list


def auto_get_mod_name(mod_file):
    mod_name = os.path.splitext(mod_file)[0]
    mod_name = mod_name.replace("_", " ").replace("-", " ").replace("+", " ")
    list_ = mod_name.split(" ")
    mod_name = ""
    n = 0
    for i in list_:
        flag = True
        n += 1
        if n > 1:
            for del_item in mod_name_del_key_list:
                if del_item["type"] == "regex":
                    if re.match(del_item["pattern"], i):
                        flag = False
                elif del_item["type"] == "string":
                    if i.lower() == del_item["pattern"]:
                        flag = False

        if flag:
            mod_name += i + " "
        # else:
        # print("del", i, mod_name)
    # print(list_, mod_name)

    mod_name = " ".join([word.capitalize() for word in mod_name.split()])
    return mod_name


def search_in_mcmod(mod_name):
    def get_mcmod_url(keywords):
        keywords = keywords.strip('\n')
        mcmod_url = re.sub(r'^', 'https://search.mcmod.cn/s?key=', keywords)
        mcmod_url = re.sub(r'\s', '+', mcmod_url)
        return mcmod_url + "&filter=1&mold="

    mcmod_url = get_mcmod_url(mod_name)

    content = requests.get(url=mcmod_url, timeout=5)

    soup = BeautifulSoup(content.content, "html.parser")
    news_results = soup.find_all("div", class_="result-item")
    mod_list = []
    for result in news_results:
        title = result.find("div", class_="head").text.strip()
        link = str(result.find("div", class_="foot").find("span", class_="info").find("a").get("href"))
        if not (link.startswith("http") or link.startswith("https")):
            link = "https://" + link
        mod_list.append({"title": title, "link": link})
    return mod_list


def search_in_bing(mod_name):
    def get_bing_url(keywords):
        keywords = keywords.strip('\n')
        bing_url = re.sub(r'^', 'https://cn.bing.com/search?q=', keywords)
        bing_url = re.sub(r'\s', '+', bing_url)
        return bing_url + "&Accept-Language=zh-CN"

    bing_url = get_bing_url(mod_name + " site:mcmod.cn/class")

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:81.0) Gecko/20100101 Firefox/81.0',
               'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
               'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
               'Accept-Encoding': 'gzip, deflate',
               'cookie': 'DUP=Q=sBQdXP4Rfrv4P4CTmxe4lQ2&T=415111783&A=2&IG=31B594'
                         'EB8C9D4B1DB9BDA58C6CFD6F39; MUID=196418ED32D66077102115'
                         'A736D66479; SRCHD=AF=NOFORM; SRCHUID=V=2&GUID=DDFFA87D3'
                         'A894019942913899F5EC316&dmnchg=1; ENSEARCH=BENVER=1; _H'
                         'PVN=CS=eyJQbiI6eyJDbiI6MiwiU3QiOjAsIlFzIjowLCJQcm9kIjoi'
                         'UCJ9LCJTYyI6eyJDbiI6MiwiU3QiOjAsIlFzIjowLCJQcm9kIjoiSCJ'
                         '9LCJReiI6eyJDbiI6MiwiU3QiOjAsIlFzIjowLCJQcm9kIjoiVCJ9LC'
                         'JBcCI6dHJ1ZSwiTXV0ZSI6dHJ1ZSwiTGFkIjoiMjAyMC0wMy0xNlQwM'
                         'DowMDowMFoiLCJJb3RkIjowLCJEZnQiOm51bGwsIk12cyI6MCwiRmx0'
                         'IjowLCJJbXAiOjd9; ABDEF=V=13&ABDV=11&MRNB=1614238717214'
                         '&MRB=0; _RwBf=mtu=0&g=0&cid=&o=2&p=&c=&t=0&s=0001-01-01'
                         'T00:00:00.0000000+00:00&ts=2021-02-25T07:47:40.5285039+'
                         '00:00&e=; MUIDB=196418ED32D66077102115A736D66479; SerpP'
                         'WA=reg=1; SRCHUSR=DOB=20190509&T=1614253842000&TPC=1614'
                         '238646000; _SS=SID=375CD2D8DA85697D0DA0DD31DBAB689D; _E'
                         'DGE_S=SID=375CD2D8DA85697D0DA0DD31DBAB689D&mkt=zh-cn; _'
                         'FP=hta=on; SL_GWPT_Show_Hide_tmp=1; SL_wptGlobTipTmp=1;'
                         ' dsc=order=ShopOrderDefault; ipv6=hit=1614260171835&t=4'
                         '; SRCHHPGUSR=CW=993&CH=919&DPR=1&UTC=480&WTS=6374985064'
                         '2&HV=1614256571&BRW=HTP&BRH=M&DM=0'
               }

    content = requests.get(url=bing_url, timeout=5, headers=headers)

    soup = BeautifulSoup(content.content, "html.parser")
    news_results = soup.find_all("li", class_="b_algo")
    mod_list = []
    for result in news_results:
        title = "-".join(result.find("h2").text.strip().split("-")[:-1])
        link = str(result.find("cite").text.strip())
        if not (link.startswith("http") or link.startswith("https")):
            link = "https://" + link
        mod_list.append({"title": title, "link": link})
    return mod_list


def levenshtein_distance(s1, s2):
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    # s1 is now the longer string
    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


def string_similarity(str1, str2):
    dist = levenshtein_distance(str1, str2)
    max_len = max(len(str1), len(str2))
    if max_len == 0:
        return 1.0
    similarity = 1 - dist / max_len
    return similarity


def auto_search_mod_name(mod_name):
    list_ = []
    for mod in search_in_mcmod(mod_name):
        if any('\u4e00' <= char <= '\u9fff' for char in mod["title"]):
            mod["title"] = mod["title"].split("(")[-1].split(")")[0]

        mod["similarity"] = string_similarity(mod_name, mod["title"])
        list_.append(mod)

    # 如果匹配度都不高使用bing再次搜索
    if len(list_) == 0 or max([mod["similarity"] for mod in list_]) < 0.5:
        for mod in search_in_bing(mod_name):
            if any('\u4e00' <= char <= '\u9fff' for char in mod["title"]):
                mod["title"] = mod["title"].split("(")[-1].split(")")[0]
            mod["similarity"] = string_similarity(mod_name, mod["title"])
            list_.append(mod)

    # 排序
    list_.sort(key=lambda x: x["similarity"], reverse=True)

    return list_[0] if len(list_) > 0 else None


def auto_get_renamed(mod_mod_link, raw_mod_file_name):
    try:
        soup = BeautifulSoup(requests.get(mod_mod_link).text, "html.parser")
        chinese_name = soup.find("div", class_="class-title").find("h3").text.strip()
    except:
        chinese_name = ""

    rename = raw_mod_file_name
    if any('\u4e00' <= char <= '\u9fff' for char in chinese_name):
        rstr = r"[\/\\\:\*\?\"\<\>\|]"
        chinese_name = re.sub(rstr, "_", chinese_name)
        if not raw_mod_file_name.startswith("["+chinese_name) and len(chinese_name) > 0:
            rename = "[%s]%s" % (chinese_name, raw_mod_file_name)

    return rename


def search_duplicate_mod(mod_list):
    # 搜索重复mod
    list_ = []
    del_list = []
    for mod in mod_list:
        if mod["title"] in list_:
            del_list.append(mod)
            mod_list.remove(mod)
        else:
            list_.append(mod["title"])

    return del_list




def main():
    mod_file_list = get_mod_file_list(input_path)
    print(f"共找到{len(mod_file_list)}个mod文件")

    print("开始自动获取mod名称")
    mod_name_list = []
    for mod_file in tqdm(mod_file_list, desc="获取mod名称"):
        mod_name = auto_get_mod_name(mod_file)
        mod_name_list.append({"file": mod_file, "name": mod_name})

    print("自动获取mod名称完成")
    print(f"分别是{', '.join([mod['name'] for mod in mod_name_list])}")

    print("开始自动获取mc百科搜索结果")

    mod_list = []

    for mod_name in tqdm(mod_name_list, desc="获取mc百科搜索结果"):
        mod_list.append(auto_search_mod_name(mod_name["name"]))
        mod_list[-1]["mod_file"] = mod_name["file"]
        time.sleep(random.random()*1.5)

    print("自动获取mc百科搜索结果完成")
    print(
        f"分别是{', '.join([mod['title'] + '(相似度: %s' % round(mod['similarity'] * 100, 2) + '%)' for mod in mod_list])}")

    print("开始自动搜索重复mod")

    # for mod in mod_list:
    #     mod["mod_file"] = os.path.join(input_path, mod["mod_file"])

    del_list = search_duplicate_mod([{"title": mod["title"], "mod_file": os.path.join(input_path, mod["mod_file"])} for mod in mod_list])

    print("自动搜索重复mod完成")

    print(f"分别是{', '.join([mod['title'] for mod in del_list])}")

    for mod in tqdm(del_list, desc="删除重复mod"):
        if input("删除%s? (y/n): " % mod["title"]) == "y":
            os.remove(mod["mod_file"])
        for mod2 in mod_list:
            if mod["title"] == mod2["title"]:
                mod_list.remove(mod2)
    print("删除完成")

    if rename:
        print("开始自动重命名mod")
        for mod in tqdm(mod_list, desc="自动重命名mod"):
            os.rename(os.path.join(input_path, mod["mod_file"]), os.path.join(input_path, auto_get_renamed(mod["link"], os.path.basename(mod["mod_file"]))))
            print(f"重命名{os.path.basename(mod['mod_file'])}为{auto_get_renamed(mod['link'], os.path.basename(mod['mod_file']))}")
            time.sleep(random.random())
        print("自动重命名mod完成")

    print("运行结束")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="""AutoMcModsDeDup - 一个MC全自动检查mod重复以及自动格式化mod名称的脚本""")
    parser.add_argument("-i", "--input_path", type=str, help="输入文件夹")
    parser.add_argument("-o", "--output_path", type=str, help="输出文件夹")
    parser.add_argument("-r", "--rename", action="store_true", help="自动重命名mod")
    args = parser.parse_args()
    if args.input_path is None:
        input_path = input("请输入输入文件夹路径：")
    else:
        input_path = args.input_path
    if args.output_path is None:
        output_path = input("请输入输出文件夹路径(不输入默认更改原文件夹)：")
    else:
        output_path = args.output_path
    if args.rename:
        rename = True
    else:
        rename = False

    print("开始运行")
    if output_path == "":
        output_path = input_path
    else:
        os.makedirs(output_path, exist_ok=True)
        # 复制input
        shutil.copytree(input_path, output_path)
        input_path = output_path

    print(f"输入文件夹路径为{input_path}")
    main()
