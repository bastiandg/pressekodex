#!/usr/bin/python3

from goose3 import Goose
import os
import re
import requests
import argparse
import subprocess
from llm_helper import initLlm, getLlmReply
import sys
from dotenv import load_dotenv
import json
from bs4 import BeautifulSoup


systemMessageFile = "prompts/system-message.md"
model = None
PANDOC_COMMAND = ['pandoc', '-f', 'gfm', '-t', 'html', '-o']
DOMAIN_PATTERN = r"^(?:https?:\/\/)?(?:www\.)?([^\/]+)"


def convertMdToHtml(md, htmlFilename):
    process = subprocess.Popen(
        PANDOC_COMMAND + [htmlFilename],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    pandocOutput, error = process.communicate(input=md.encode())


def openBrowser(filename):
    try:
        subprocess.Popen(['firefox', filename], start_new_session=True)
    except Exception as e:
        print(f"An error occurred: {e}")


def downloadImage(article, filenameBase):
    if 'opengraph' not in article.infos.keys() \
            or 'image' not in article.infos['opengraph'].keys() \
            or article.infos['opengraph']['image'] == "":
        return None
    if isinstance(article.infos['opengraph']['image'], str):
        imageUrl = article.infos['opengraph']['image']
    else:
        imageUrl = article.infos['opengraph']['image'][0]
    imageUrlParameters = imageUrl.split("?")
    imageExtension = imageUrlParameters[0].split("/")[-1].split(".")[-1]
    filename = f"{filenameBase.replace(' ', '-')}.{imageExtension}"
    try:
        response = requests.get(imageUrl, stream=True)

        if response.status_code == 200:
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            return filename
        else:
            return None
    except requests.exceptions.RequestException:
        return None


def harmcheck(article, filenameBase):
    harmcheckReply = getLlmReply(
        promptName=f"Checking for harms in \"{article.title}\"",
        promptTemplateFile="prompts/harmcheck.md",
        outputFilename=f"{filenameBase}-harmcheck.md",
        templateStringVariables={
            "article": article.cleaned_text,
            "url": article.canonical_link,
            "title": article.title
        }
    )
    pattern = r"^\*?\*?Harmful Content\*?\*?:.*(No|Yes).*$"
    match = re.search(pattern, harmcheckReply, re.MULTILINE | re.IGNORECASE)

    if match:
        harmful_text = match.group(1).lower()
        harmful = (harmful_text == "yes")
    else:
        harmful = False
    return harmful, harmcheckReply


def init():
    global model
    global url
    global articleBaseDir

    load_dotenv()

    parser = argparse.ArgumentParser(description='Process arguments.')

    parser.add_argument('url', type=str, help='The URL to process')
    parser.add_argument('--article-base-dir', type=str, default=f"{os.environ.get('HOME')}/articles", help='Base directory for articles.')

    args = parser.parse_args()

    url = args.url
    articleBaseDir = args.article_base_dir
    with open(systemMessageFile, 'r') as file:
        systemMessage = file.read()
    initLlm(systemMessage)

    print(f'URL: {url}')
    print(f'Article base directory: {articleBaseDir}')


def niusExtract(article):
    html = article._raw_html
    soup = BeautifulSoup(html, 'html.parser')
    contentJsonString = soup.find('script', id='__NEXT_DATA__').text
    contentArray = json.loads(contentJsonString)["props"]["pageProps"]["_article"]["data"]["content"]
    content = ""
    for element in contentArray:
        if element["type"] == "HTML":
            content += element["data"]
    soup = BeautifulSoup(content, 'html.parser')
    return soup.get_text()


init()
g = Goose()
article = g.extract(url=url)
match = re.search(DOMAIN_PATTERN, url)
domain = match.group(1)

articleDir = f"{articleBaseDir}/{domain}"

os.makedirs(articleDir, exist_ok=True)

filenameBase = re.sub(r"[^\w\- ]+", "", article.title)
filenameBase = re.sub(r" +", " ", filenameBase)
if len(filenameBase) > 50:
    filenameBase = filenameBase[:50]
filenameBase = filenameBase.strip()
filenameBase = f"{articleDir}/{filenameBase}"

with open(filenameBase + ".txt", 'w') as f:
    f.write(article.cleaned_text)

if domain != "nius.de":
    articleText = article.cleaned_text
else:
    articleText = niusExtract(article)

with open("sections/01.txt", 'r') as file:
    pressekodex_section = file.read()
imageFilename = downloadImage(article, filenameBase)

complianceReply = getLlmReply(
    promptName=f"Compliance Check article \"{article.title}\"",
    promptTemplateFile="prompts/compliance.md",
    templateStringVariables={
        "pressekodex_section": pressekodex_section,
        "article": articleText,
        "title": article.title
    },
    outputFilename=f"{articleDir}/01.txt"
)

print(complianceReply)
