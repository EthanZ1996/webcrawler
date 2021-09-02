import requests
from sys import argv
from colorama import Fore, init
from urllib.parse import urlparse, urljoin, urlunparse
from bs4 import BeautifulSoup
import threading

# setting color variables
init(convert=True)
GREEN = Fore.GREEN
GRAY = Fore.LIGHTCYAN_EX
RESET = Fore.RESET
YELLOW = Fore.YELLOW
MAGNETA = Fore.MAGENTA
RED = Fore.RED

# sets to contain unique internal and external domain links
int_links = set()
ext_links = set()


# #Input stream clearing
# def flush_input():
#     try:
#         import msvcrt
#         while msvcrt.kbhit():
#             msvcrt.getch()
#     except ImportError:
#         import sys, termios    #for linux/unix
#         termios.tcflush(sys.stdin, termios.TCIOFLUSH)

# Converting URL into a valid form and checking for redirections
def urlValidator(url):
    parsed = urlparse(url)
    while 1:
        try:
            response = requests.get(url)
        except requests.exceptions.MissingSchema:
            parsed = parsed._replace(scheme='https')
            url = urlunparse(parsed)
            if url.find(':///', 0, 9) >= 0: url = url.replace(':///', '://')
        except requests.exceptions.SSLError:
            parsed = parsed._replace(scheme='http')
            url = urlunparse(parsed)
            if url.find(':///', 0, 9) >= 0: url = url.replace(':///', '://')
        except Exception as e:
            print(e.__class__)
            break
        else:
            print()
            if url != response.url:
                print(f"{GRAY}[*] Redirecting Link to: {response.url}{RESET}")
            url = response.url
            parsed = urlparse(url)
            url = parsed.scheme + '://' + parsed.netloc + parsed.path
            url = url.rstrip('/')
            return (url)


# to check wheather the link is valid URL or not
def isValid(link):
    parsed = urlparse(link)
    return bool(parsed.netloc) and bool(parsed.scheme)


def getWebsitesFromUrl(url):
    global int_links
    global ext_links
    global unvisitedlist
    global urls
    temSetOfIntLinks = int_links.copy()
    urls = set()                                                      #set() 函数创建一个无序不重复元素集
    domainName = urlparse(url).netloc
    soup = BeautifulSoup(requests.get(url).content, 'html5lib')

    # find all the anchor tags from the webpage and then extract the href attributes
    # for redirects in soup.findAll('location.href')
    for a_tag in soup.findAll('a'):
        href = a_tag.attrs.get('href')
        if href == '' or href is None:
            # href empty tag
            continue

        # join the URL is it's relative (like /search)
        href = urljoin(url, href)

        parsed_href = urlparse(href)
        # remove all GET parameters from, URL fragments etc.
        href = parsed_href.scheme + '://' + parsed_href.netloc + parsed_href.path
        href = href.rstrip('/')
        if not isValid(href):
            # not a valid url
            continue

        if href in int_links:
            # already in the set
            continue

        if domainName not in href:
            # external link
            if href not in ext_links:
                print(f"{MAGNETA}[*] External Link: {href}{RESET}")
                ext_links.add(href)
            continue

        urls.add(href)
        print(f"{GREEN}[*] Internal Link: {href}{RESET}")
        int_links.add(href)

    # To remove already added links from the current urls set from internal links set
    urls = urls - temSetOfIntLinks
    # unvisitedlist.extend(urllist(urls))
    # unvisitedlist = unvisitedlist - visitedlist
    return urls          #, unvisitedlist



# number of urls visited will be stored here
totalVisitedUrls = 0

# crawl the current webpage and extract links recursively
'''
maxUrls is set to 30 because if we don't keep it limited then it might take
a lot of time for big sites
'''


def crawlPage(url, maxUrls):
    global totalVisitedUrls
    global links
    totalVisitedUrls += 1

    print()
    print(f"{YELLOW}[*] Crawling: {url}{RESET}")
    links = getWebsitesFromUrl(url)
    visitedlist.append(url)

    for link in links:
        if totalVisitedUrls >= maxUrls:
            break
        crawlPage(link, maxUrls)


unvisitedlist = []
visitedlist = []
urllist = []
tmplist = []
depthDict = {}

# 线程列表
tlist = []

# def unvisitedTovisited(unvisitedlist):
#     if len(unvisitedlist):                           #if the list is not none, then keep going
#         crawlPage(unvisitedlist.pop(), maxUrls)


# # 获取指定url中的所有url，并加入到待爬列表中，作为线程的target
# def getSonPageUrl(url):
#     subList = getWebsitesFromUrl(url)
#     for u in subList:
#         if u not in depthDict:
#             depthDict[u] = depthDict[url] + 1
#             tmplist.append(u)
#
#
# def getUrls(depth):
#     # 当还有待爬网页或者还有运行中的线程
#     while ((len(tmplist) > 0) or (threading.activeCount() > 1)):
#         while len(tmplist) == 0:
#             continue
#         url = tmplist.pop(0)
#         urlList.append(url)
#         # print(threading.activeCount(),"\t" * depthDict[url], "#%d:%s" % (depthDict[url], url))
#         if depthDict[url] < depth:
#             t = threading.Thread(target=getSonPageUrl, args=(url,))
#             tlist.append(t)
#             t.start()


if __name__ == "__main__":

    intLinkFile = open('InternalLinks.txt', 'w')
    extLinkFile = open('ExternalLinks.txt', 'w')

    url = ''
    maxUrls = 0
    if len(argv) > 1:
        url = argv[1]
        maxUrls = int(argv[2])
    else:
        url = input("Enter the base URL: ")
        # while 1:
        #     try:
        #         maxUrls = int(input("Enter number of max links to Crawl: "))
        #         if (maxUrls <= 0):
        #             raise
        #     except:
        #         print(f'{RED}[ERROR]: Please Enter Integer value greater than 0{RESET}')
        #     else: break

    url = urlValidator(url)
    unvisitedlist.append(url)
    int_links.add(url)
    crawlPage(url, maxUrls)
    # unvisitedlist.append()
    urllist = list(urls)
    unvisitedlist.extend(urllist)
    unvisitedlist = list(set(unvisitedlist) - set(visitedlist))

    while len(unvisitedlist) > 0:
        for unvisitedurl in unvisitedlist:
            unvisitedlist.append(unvisitedurl)
            crawlPage(unvisitedurl, maxUrls)
            urllist = list(urls)
            unvisitedlist.extend(urllist)
            unvisitedlist = list(set(unvisitedlist) - set(visitedlist))



    # depthDict[url] = 0
    # tmplist.append(url)
    # int_links.add(url)
    # crawlPage(url, maxUrls)
    # getUrls(3)
    # int_links.remove(url)

    # for link in int_links:
    #     intLinkFile.write(link)
    #     intLinkFile.write('\n')
    #
    # for link in ext_links:
    #     extLinkFile.write(link)
    #     extLinkFile.write('\n')

    print()
    print('[*]Total Crawled URLS:', totalVisitedUrls)
    print('[*]Total Internal Links:', len(int_links))
    print('[*]Total External Links:', len(ext_links))
    print()

    # flush_input()
    input('Enter any key to Exit...')