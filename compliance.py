#!/usr/bin/python3

import argparse
import json
import os
import queue
import re
import requests
import subprocess
import sys
import threading
import traceback

from bs4 import BeautifulSoup
from dotenv import load_dotenv
from goose3 import Goose
from llm_helper import getLlmReply


systemMessage = None
systemMessageFile = "prompts/system-message.md"
MODELS = ["haiku", "sonnet", "opus", "gpt4"]
model = None
maxThreads = 0
totalCost = 0
totalCostLock = threading.Lock()
complianceReplies = []
complianceRepliesLock = threading.Lock()
errorList = []


def openBrowser(filename):
    try:
        subprocess.Popen(['firefox', filename], start_new_session=True)
    except Exception as e:
        print(f"An error occurred: {e}")


def init():
    global model
    global url
    global articleBaseDir
    global systemMessage
    global maxThreads

    load_dotenv()
    if "ANTHROPIC_API_KEY" not in os.environ and "OPENAI_API_KEY" not in os.environ:
        print("Either ANTHROPIC_API_KEY or OPENAI_API_KEY has to be set in .env file", file=sys.stderr)
        sys.exit(1)
    parser = argparse.ArgumentParser(description='Process arguments.')

    parser.add_argument('url', type=str, help='The URL to process')
    parser.add_argument('--article-base-dir', type=str, default=f"{os.environ.get('HOME')}/articles", help='Base directory for articles.')
    parser.add_argument('--model', type=str, default="haiku", help=f"LLM used for the evaluation. Possible values: {MODELS}")
    parser.add_argument('--max-threads', type=int, default=2, help="Max number of threads to create")

    args = parser.parse_args()
    url = args.url
    model = args.model
    maxThreads = args.max_threads
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


def generateHtmlTable(headers, data):
    html = "<table border='1' cellpadding='5' cellspacing='0'>\n"
    html += "  <tr>\n"
    for header in headers:
        html += f"    <th>{header}</th>\n"
    html += "  </tr>\n"

    for item in data:
        html += "  <tr>\n"
        for header in headers:
            if header == "compliant":
                compliantValue = "yes" if item[header] else "no"
                color = "#66FF66" if item[header] else "#FF6666"
                html += f"    <td style='background-color: {color}; font-weight: bold; text-align: center;'>{compliantValue}</td>\n"
            else:
                if isinstance(item[header], str):
                    cellContent = item[header].replace('\n', '<br>')
                else:
                    cellContent = item[header]
                html += f"    <td>{cellContent}</td>\n"
        html += "  </tr>\n"

    html += "</table>"
    return html


def processComplianceReply(sectionNumber, sectionTitle, complianceReply):
    soup = BeautifulSoup(complianceReply, "lxml")
    isCompliantString = re.sub(r'[\s\n]+', "", soup.find("compliant").text)
    isCompliant = isCompliantString.lower() == "yes"
    reasoning = soup.find("reasoning").text.strip()
    processedReply = {
        "ziffer": sectionNumber,
        "title": sectionTitle,
        "compliant": isCompliant,
        "reasoning": reasoning
    }
    return processedReply


def extractArticle(url):
    g = Goose()
    article = g.extract(url=url)
    match = re.search(r"^(?:https?:\/\/)?(?:www\.)?([^\/]+)", url)
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
        shortTitle = "-".join(titleWords[:5])
    articleDir = f"{articleBaseDir}/{domain}/{shortTitle}"
    os.makedirs(articleDir, exist_ok=True)
    with open(f"{articleDir}/article.txt", 'w') as f:
        f.write(articleText)
    return articleText, title, articleDir


def evaluateSection(sectionNumber, articleText, articleTitle, articleDir):
    global totalCost
    global complianceReplies
    pressekodexSectionPath = f"selected-sections/{sectionNumber:02d}.txt"
    evaluationFilename = f"{articleDir}/{sectionNumber:02d}.txt"
    if not os.path.exists(pressekodexSectionPath):
        return
    with open(pressekodexSectionPath, 'r') as file:
        pressekodexSection = file.read()
    sectionTitle = pressekodexSection.split('\n')[0].split(" – ")[-1]

    if not os.path.exists(evaluationFilename):
        complianceReply, callCost = getLlmReply(
            modelClass=model,
            promptName=f"Compliance Check for pressekodex section {sectionNumber} article \"{articleTitle}\"",
            promptTemplateFile="prompts/compliance.md",
            systemMessage=systemMessage,
            templateStringVariables={
                "pressekodex_section": pressekodexSection,
                "article": articleText,
                "title": articleTitle
            },
            outputFilename=evaluationFilename
        )
        print(f"Cost: {callCost}")
        with totalCostLock:
            totalCost += callCost
    else:
        with open(evaluationFilename, 'r') as file:
            complianceReply = file.read()
    processedReply = processComplianceReply(sectionNumber, sectionTitle, complianceReply)
    with complianceRepliesLock:
        complianceReplies.append(processedReply)


def sectionWorker(sectionQueue, articleText, articleTitle, articleDir):
    while True:
        task = sectionQueue.get()
        if task is None:
            # None is the signal to stop
            break
        try:
            evaluateSection(task, articleText, articleTitle, articleDir)
        except Exception as e:
            print(f"Error on task \"{task[0]}\": {e}")
            traceback.print_exc()
            errorList.append((task[0], str(e)))
        finally:
            sectionQueue.task_done()


def processSections(articleText, articleTitle, articleDir):
    threads = []
    sectionQueue = queue.Queue()
    for i in range(1, 17):
        sectionQueue.put(i)
    for _ in range(maxThreads):
        thread = threading.Thread(target=sectionWorker, args=(sectionQueue, articleText, articleTitle, articleDir))
        thread.start()
        threads.append(thread)
    sectionQueue.join()

    for _ in threads:
        sectionQueue.put(None)
    for thread in threads:
        thread.join()
    if errorList:
        print("Errors encountered:")
        for task, err in errorList:
            print(f"Task {task}: {err}")


def main():
    init()
    articleText, articleTitle, articleDir = extractArticle(url)
    processSections(articleText, articleTitle, articleDir)

    tableHeaders = ["ziffer", "title", "compliant", "reasoning"]
    complianceTable = generateHtmlTable(tableHeaders, sorted(complianceReplies, key=lambda x: x["ziffer"]))
    complianceResultFile = f"{articleDir}/compliance-table.html"

    html = f"<h1>{articleTitle}</h1>\n<b>URL:</b> {url}\n<br><br>{complianceTable}"

    with open(complianceResultFile, 'w') as f:
        f.write(html)
    openBrowser(complianceResultFile)
    print(f"\ntotalCost: {totalCost:.2f} $")
    return 0


if __name__ == '__main__':
    sys.exit(main())
