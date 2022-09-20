from bs4 import BeautifulSoup as html
import requests
import os 
import argparse
import sys


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


def download_img(img_src, root_path):
    len_in_folder = len(os.listdir(root_path))
    for idx, src in enumerate(img_src, len_in_folder):
        img = requests.get(src)
        extension = src.split(".")[-1]
        if root_path[-1] != "/":
            root_path += "/"
        path_save = f"{root_path}{idx}.{extension}"
        with open(path_save, "wb") as img_content:
            img_content.write(img.content)
            img_content.close()
        print_progress(idx+1-len_in_folder, len(img_src), fi=root_path, last=path_save)


def get_img_from_url(param):
    r = requests.get(param.url)
    page = html(r.content, "html.parser")
    soup = page.find(param.element, {param.type: param.value})
    all_img = soup.find_all("img")
    img_src = [i["src"] for i in all_img][1:]
    download_img(img_src, param.path)


def main():
    
    parser = argparse.ArgumentParser(description="Clone Image From Website", formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-u", "--url", type=str, help="Url website need to find", required=True)
    parser.add_argument("-e", "--element", type=str, help="Root element need to find", required=True)
    parser.add_argument("-t", "--type", type=str, help="Attribute of element need to find. 'class' or 'id'", required=True)
    parser.add_argument("-v", "--value", type=str, help="Value of the attribute need to find", required=True)
    parser.add_argument("-p", "--path", type=str, help="Path to save image after download", required=True)

    args = parser.parse_args()
    get_img_from_url(args)


if __name__ == "__main__":
    main()
