import re
from urllib.parse import urlparse
from urllib.parse import urlunparse
from bs4 import BeautifulSoup # TODO Cite https://www.crummy.com/software/BeautifulSoup/bs4/doc/
import pickle
import os

def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content

    if not is_valid(url):
        print("Bad Link")
        return []
    
    if resp.status != 200:
        print("Bad Code")
        return []
    
    bsObject = BeautifulSoup(resp.raw_response.content, "html.parser")
    linkSet = set()

    # TODO TODO TODO Cite https://www.crummy.com/software/BeautifulSoup/bs4/doc/
    webpageText = bsObject.get_text()
    textList = str(webpageText).strip().split()

    if len(textList) < 100:
        print("Too Short")
        return []

    # TODO Check for longest
    

    with open('visitedLinks.txt', 'a+') as linkFile:
        linkFile.seek(0)
        visited = [line.rstrip() for line in linkFile]
        
        ## TODO TODO TODO cite this properly to ensure academic honesty
        for link in bsObject.find_all('a'):
            newURL = link.get('href')

            if is_valid(newURL):

                #TODO Cite https://docs.python.org/3/library/urllib.parse.html
                parsedLink = urlparse(newURL)
                parsedLink._replace(fragment="")
                newURL = parsedLink.geturl()
    
                newURL = re.sub(r'www\.', "", newURL)
                
                
                if newURL not in visited:
                    linkSet.add(newURL)

                    # print(url)
                    visited.append(newURL)
                    linkFile.write(newURL + '\n')
            else: 
                pass

    return list(linkSet)

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        
        if parsed.scheme not in set(["http", "https"]):
            return False

        #TODO TODO fix cecs.uci.edu
        if not (re.search(r"ics.uci.edu", parsed.netloc.lower()) or re.search(r"cs.uci.edu", parsed.netloc.lower()) or re.search(r"informatics.uci.edu", parsed.netloc.lower()) or re.search(r"stat.uci.edu", parsed.netloc.lower())):
            return False

        if "tag" in parsed.query.lower(): # Keyword Reference Pages
            return False
        if "day" in parsed.query.lower() or "date" in parsed.query.lower() or "week" in parsed.query.lower() or "month" in parsed.query.lower() or "event" in parsed.query.lower(): # Characteristic of calendar traps
            return False
        
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise
