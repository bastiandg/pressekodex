#!/usr/bin/python3

from goose3 import Goose
import os
import re
import requests
import argparse
import subprocess
from llm_helper import getLlmReply
# import sys
from dotenv import load_dotenv
import json
from bs4 import BeautifulSoup


systemMessage = None
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


def downloadImage(article, downloadDirectory):
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
    filename = f"{downloadDirectory}/cover.{imageExtension}"
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


def init():
    global model
    global url
    global articleBaseDir
    global systemMessage

    load_dotenv()

    parser = argparse.ArgumentParser(description='Process arguments.')

    parser.add_argument('url', type=str, help='The URL to process')
    parser.add_argument('--article-base-dir', type=str, default=f"{os.environ.get('HOME')}/articles", help='Base directory for articles.')

    args = parser.parse_args()

    url = args.url
    articleBaseDir = args.article_base_dir
    with open(systemMessageFile, 'r') as file:
        systemMessage = file.read()

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

if domain != "nius.de":
    articleText = article.cleaned_text
else:
    articleText = niusExtract(article)

title = re.sub(r"[^\w\- ]+", "", article.title)
title = re.sub(r" +", " ", title)
title = title.strip()
titleWords = title.split(" ")
if len(titleWords) > 5:
    title = "-".join(titleWords[:5])
articleDir = f"{articleBaseDir}/{domain}/{title}"
os.makedirs(articleDir, exist_ok=True)

with open(f"{articleDir}/article.txt", 'w') as f:
    f.write(articleText)
imageFilename = downloadImage(article, articleDir)

totalCost = 0

for i in range(1, 17):
    pressekodexSectionPath = f"selected-sections/{i:02d}.txt"
    evaluationFilename = f"{articleDir}/{i:02d}.txt"
    if not os.path.exists(pressekodexSectionPath):
        continue
    with open(pressekodexSectionPath, 'r') as file:
        pressekodexSection = file.read()
    sectionTitle = pressekodexSection.split('\n')[0]

    if not os.path.exists(evaluationFilename):
        complianceReply, callCost = getLlmReply(
            modelClass="haiku",
            promptName=f"Compliance Check for pressekodex section {i} article \"{article.title}\"",
            promptTemplateFile="prompts/compliance.md",
            systemMessage=systemMessage,
            templateStringVariables={
                "pressekodex_section": pressekodexSection,
                "article": articleText,
                "title": article.title
            },
            outputFilename=evaluationFilename
        )
        print(f"Cost: {callCost}")
        totalCost += callCost
    else:
        with open(evaluationFilename, 'r') as file:
            complianceReply = file.read()
    soup = BeautifulSoup(complianceReply, "lxml")
    isCompliantString = re.sub(r'[\s\n]+', "", soup.find("compliant").text)
    isCompliant = isCompliantString.lower() == "yes"
    print(f"{sectionTitle}: {isCompliant}")


print(f"\ntotalCost: {totalCost}")
