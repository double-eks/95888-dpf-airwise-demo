"""
This is the main structure of web scraping
"""


import logging
import re
from datetime import datetime
from urllib.request import urlopen

import numpy as np
import pandas as pd
from bs4 import BeautifulSoup, Tag

from console import Console


def genLogger(name: str, formatting: str, level: int = logging.DEBUG):
    if (name == ''):
        raise Exception('invalid logger name')
    logger = logging.getLogger(name)
    logger.setLevel(level)
    ch = logging.StreamHandler()
    ch.setLevel(level)
    formatter = logging.Formatter(formatting, datefmt='%H:%M')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger


def webScraping(url: str, path: str) -> BeautifulSoup:

    print('')
    # Format the loading messages
    domain, home = findDomian(url)
    processing = f'web scraping from {home}'
    processed = f'{domain} data collected'

    # Start web scraping
    console.loading(processing, '>')
    html = urlopen(url)
    # bs = BeautifulSoup(html.read(), "lxml")
    with open(path) as copy:
        html = copy.read()
    bs = BeautifulSoup(html, "html.parser")
    # Complete web scraping
    console.loading(processed, '<')
    return bs


def findDomian(url: str):
    """
    Return the domain and home page link of the given url
    """
    link = url[re.search('https://', url).end():]
    home = link.split('/')[0]
    domain = home.split('.')[1]
    return domain, home


def findSubItem(tag: Tag, itemTag: str, itemName: str) -> Tag:
    for subTag in tag.find_all_next(itemTag):
        if (subTag.text.strip().lower() == itemName.lower()):
            return subTag


def isValidText(text: str):
    text = text.strip()
    if (len(text) <= 1) or (not text[0].isalnum()):
        return False
    else:
        return True


def selTrigger(triggersListTag: Tag, triggersList: list, triggerIndex: int):
    """
    Generate report for the selected trigger, including About and Actions
    Args:
        triggersListTag (Tag): tag of the trigger ul
        triggersList (list): storing trigger options
        triggerIndex (int): user response - 1 as the index
    """
    header = findSubItem(triggersListTag, 'h2', triggersList[triggerIndex])
    about, action = header.find_all_next('h3', limit=2)
    actionDetail = about.find_next('ul')
    # Report the About part
    console.para(about.text)
    for tag in about.find_all_next():
        if ('h' in tag.name):
            break
        if (('p' or 'li') in tag.name):
            if (isValidText(tag.text)):
                console.para(tag.text.strip())
    # Report the Action You Can Take part
    console.title(action.text)
    for detail in (actionDetail.stripped_strings):
        if (isValidText(detail)):
            console.bullet(detail)


def prologue():
    # Scrap essential info
    clearAir = 'WELCOME to ClearAir for Better Asthma Management'
    date = datetime.now().strftime(console.fmtDate)
    time = datetime.now().strftime(console.fmtTime)
    brief = '\t'.join([date, time])
    epaIntro = ''
    for para in epa.find('article').find_all('p'):
        if (len(para.attrs) == 0):
            epaIntro = para.string.strip()
            break
    # Output to Console
    console.header(clearAir)
    console.subHeader(brief)
    console.para(epaIntro)


def triggerPage():
    console.header('Asthma Triggers © EPA')
    # Scrap essential info
    triggersListTag = epa.find('article').find('ul')
    triggersList = [s for s in triggersListTag.stripped_strings]
    # Output to Console
    console.para('More than 25 million people in the U.S. have asthma. '
                 'It is a long-term disease that causes your airways to become swollen and inflamed, '
                 'making it hard to breathe. There is no cure for asthma, '
                 'but it can be managed and controlled.')
    console.multiChoice(triggersList)
    # Ask for option and output to console
    for inputNum in range(len(triggersList)):
        selTrigger(triggersListTag, triggersList, inputNum)


def fastStatsPage():
    console.header('Asthma Faststats © CDC')
    cardTag = 'div'
    attr = 'class'
    cardClass = 'card mb-3'
    cardHeaderClass = 'bg-primary'

    for card in nchc.find_all(cardTag, attrs={attr: cardClass}):
        header = card.find_next('div')
        if (cardHeaderClass in header.get(attr)):
            console.title(header.text.strip())
            for fact in card.find_all('li'):
                console.bullet(fact.text.strip())


if __name__ == "__main__":

    # * Initialize console
    console = Console()
    logging.basicConfig(level=logging.DEBUG)

    # Web Scraping
    epaPath = '/Volumes/Workaholic/Workspace/Processing/Asthma Triggers_ Gain Control _ US EPA.html'
    epaURL = 'https://www.epa.gov/asthma/asthma-triggers-gain-control'
    epa = webScraping(epaURL, epaPath)
    nchcPath = '/Volumes/Workaholic/Workspace/Processing/FastStats - Asthma.html'
    nchcURL = 'https://www.cdc.gov/nchs/fastats/asthma.htm'
    nchc = webScraping(nchcURL, nchcPath)

    # Deploy
    prologue()
    console.homepage()
    input()
    triggerPage()
    input()
    fastStatsPage()