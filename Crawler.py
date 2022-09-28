from bs4 import BeautifulSoup as html
import requests
import os 
import argparse
import sys
import codecs
import base64
import json
import glob


ALL_EXTENSION = ["jpg", "jpeg", "png"]


def print_progress(index, total, fi="", last=""):
    percent = ("{0:.1f}").format(100 * ((index) / total))
    fill = int(30 * (index / total))
    spec_char = ["\x1b[1;31;40m╺\x1b[0m",
                 "\x1b[1;36;40m━\x1b[0m", "\x1b[1;37;40m━\x1b[0m"]
    bar = spec_char[1]*(fill-1) + spec_char[0] + spec_char[2]*(30-fill)
    if fill == 30:
        bar = spec_char[1]*fill

    percent = " "*(5-len(str(percent))) + str(percent)

    if index == total:
        print(fi + " " + bar + " " + percent + "% " + last)
    else:
        print(fi + " " + bar + " " + percent + "% " + last, end="\r")


def get_len_in_folder(root_path):
    return len(os.listdir(root_path))


def convert_base64(base64_str):
    bs64 = base64_str.split("base64,")[-1]
    bs64 = "".join(bs64.split("\n"))
    bs64 = "".join(bs64.split(" "))
    bs64 = bytes(bs64, "ascii")
    return base64.decodebytes(bs64)


def download_img(img_src, root_path):
    if root_path[-1] != "/":
        root_path += "/"
    for idx, src in enumerate(img_src):
        
        if "base64" in src:
            continue
            extension = src.split("data:image/")[1]
            extension = extension.split(";base64")[0]
            if extension not in ALL_EXTENSION:
                continue
            path_save = f"{root_path}{get_len_in_folder(root_path)}.{extension}"
            with open(path_save, "wb") as img_content:
                img_content.write(convert_base64(src))
                img_content.close()
        else:
            img = requests.get(src)
            extension = src.split(".")[-1]
            if extension not in ALL_EXTENSION:
                continue
            path_save = f"{root_path}{get_len_in_folder(root_path)}.{extension}"
            with open(path_save, "wb") as img_content:
                img_content.write(img.content)
                img_content.close()
        print_progress(idx+1, len(img_src), fi=root_path, last=path_save)


def get_data_image(img_src):
    base64_list = []
    url_list = []
    for idx, src in enumerate(img_src):
        if "base64" in src:
            extension = src.split("data:image/")[1]
            extension = extension.split(";base64")[0]
            if extension not in ALL_EXTENSION:
                continue
            base64_list.append({
                "name": f"{idx}.{extension}",
                "data": src
            })
        else:
            # print(src)
            extension = src.split(".")[-1]
            if extension not in ALL_EXTENSION:
                extension = "jpeg"
            url_list.append({
                "name": f"{idx}.{extension}",
                "url": src
            })
        print_progress(idx+1, len(img_src))
    return [base64_list, url_list]


def get_img_from_url(param):
    r = requests.get(param["url"])
    page = html(r.content, "html.parser")
    soup = page.find(param["element"], {param["type"]: param["value"]})
    all_img = soup.find_all("img")
    img_src = [i["src"] for i in all_img][1:]
    download_img(img_src, param["path"])


def save_json_data(data, file_name):
    with open(file_name, "w") as f:
        json.dump(data, f)
        f.close()
    print("[+] Save", file_name, "successfully")


def get_img_from_file(param):
    html_file = codecs.open(param["html_path"], "r", encoding='utf-8')
    page = html(html_file.read(), "html.parser")
    html_file.close()
    soup = page.find(param["element"], {param["type"]: param["value"]})
    all_img = soup.find_all("img")
    img_src = [i["src"] for i in all_img][1:]
    # download_img(img_src[20:], param["path"])
    base64_list, url_list = get_data_image(img_src)
    save_json_data(base64_list, "./json_backup/base64_list.json")
    save_json_data(url_list, "./json_backup/url_list.json")


def main():
    args = {}
    args["html_path"] = input("Path file html: ")
    args["element"] = input("Enter name of element: ")
    args["type"] = input("Enter type of element: ")
    args["value"] = input("Enter value of element: ")
    get_img_from_file(args)


def _save_base64_img(root_path, src, extension):
    path_save = f"{root_path}{get_len_in_folder(root_path)}.{extension}"
    with open(path_save, "wb") as img_content:
        img_content.write(convert_base64(src))
        img_content.close()
    return path_save


def save_base64_img(json_path, root_path):
    if root_path[-1] != "/":
        root_path += "/"
    data = open(json_path)
    data = json.load(data)
    for idx, src in enumerate(data):
        path_save = _save_base64_img(root_path, src["data"], src["name"].split(".")[-1])
        print_progress(idx+1, len(data), fi=root_path, last=path_save)


def _save_url_img(root_path, src, extension):
    img = requests.get(src)
    path_save = f"{root_path}{get_len_in_folder(root_path)}.{extension}"
    with open(path_save, "wb") as img_content:
        img_content.write(img.content)
        img_content.close()
    return path_save


def save_url_img(json_path, root_path):
    if root_path[-1] != "/":
        root_path += "/"
    data = open(json_path)
    data = json.load(data)
    for idx, src in enumerate(data):
        path_save = _save_url_img(root_path, src["url"], src["name"].split(".")[-1])
        print_progress(idx+1, len(data), fi=root_path, last=path_save)


def move_file(src_path, dst_path):
    list_image = glob.glob(os.path.join(src_path, "*"))
    for idx, _path in enumerate(list_image):
        name = _path.split("\\")[-1]
        extension = name.split(".")[-1]
        new_name = f"{get_len_in_folder(dst_path)}.{extension}"
        new_path = os.path.join(dst_path, new_name)
        os.rename(_path, new_path)
        print_progress(idx+1, len(list_image), fi=dst_path, last=new_path)


if __name__ == "__main__":
    main()
    root_path = "./dataset/Co-Do-Hue"
    save_base64_img("./json_backup/base64_list.json", root_path)
    save_url_img("./json_backup/url_list.json", root_path)
    # move_file("./dataset/Da-Lat", "./dataset/_da_lat")