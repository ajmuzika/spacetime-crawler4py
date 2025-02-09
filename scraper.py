import re # Importing Regular Expression Library (Python Software Foundation, 2025a).
from urllib.parse import urlparse # Importing Parse Library (Python Software Foundation, 2025b)
from bs4 import BeautifulSoup # Importing BeautifulSoup Library (Richardson, 2025).
import nltk # Import nltk (NLTK Project, 2024). #TODO Tell the TA in the report to install nltk

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

    try:
        
        if not is_valid(url): # If the URL is not even valid at the offset
            print("Bad Link") # Information Message to the User
            return [] # Return Empty List to prevent adding to frontier
        
        if resp.status != 200: # If the status does not allow us to crawl the page
            print("Bad Code") # Information Message to the User
            return [] # Return Empty List to prevent adding to frontier
        
        bsObject = BeautifulSoup(resp.raw_response.content, "html.parser") # Declare a BeautifulSoup object with the raw text from the webpage as a parameter and selecting the HTML parameter for parsing (Richardson, 2025).
        
        linkSet = set() # Declare a set to put in our links scraped from this URL. Set data structure to prevent duplicates
    
        webpageText = bsObject.get_text() # Extracting the raw text from the resp raw response through the BeautifulSoup object which parses through the text with this method automatically (Richardson, 2025).
        textList = str(webpageText).strip().split() # Take the text, remove the whitespace at the front or the back of the string, and split on spaces to retrieve a list of words.
        hyperlinksList = bsObject.find_all('a') # Because hyperlinks are denoted by the tag `a` in HTML, we use the command `bsObject.find_all('a')` to get the list of all hyperlinks that are present in the page (Richardson, 2025).
    
        if len(textList) < 100: # If the website has very few words and therefore has very little data we can use (value of 100 words used here)
            print("Too Short") # Information Message to the User
            return [] # Return Empty List to prevent adding to frontier

        if len(set(textList))/len(textList) < 0.10: # If the website has very high ratio of unique words to total words, then it has a cery high quantity of repeated words and it is very unlikely that useful data will be attained (ratio of 0.10 used here)
            print("Unique Words to Total Words Ratio Too Low") # Information Message to the User
            return [] # Return Empty List to prevent adding to frontier
        
        if len(hyperlinksList) / len(textList) > 0.75: # If the website has very high ratio of hyperlinks to words in the text, then it is likely a website that is only for redirects to overflow the frontier (ratio of 0.75 used here)
            print("Hyperlinks to Total Words Ratio Too High") # Information Message to the User
            return [] # Return Empty List to prevent adding to frontier
        
    
        with open('visitedLinks.txt', 'a+') as linkFile, open('tokens.txt', 'a+') as tokenFile, open('longest.txt', 'a+') as longestPageFile: # Declare and open three files -- one to hold all links that we visit in our crawl `visitedLinks.txt`, one to hold all of the tokens so that we can tokenize them as a postprocess `tokens.txt`, and one to hold the link and length in words of the longest page we come across `longest.txt`.

            # Reset the pointers of each file object to the beginning.
            linkFile.seek(0)
            tokenFile.seek(0)
            longestPageFile.seek(0)

            
            longestPage = longestPageFile.read() # Read from the text file for the longest page to see if there is anything in it
            
            if not longestPage: # If there is nothing recorded in the file
                longestPageFile.write(url + "`" + str(len(textList))) # Record the present page in the file and length in the format "{Page URL}`{Length}"

            elif (int(longestPage.split("`")[1]) < len(textList)): # If we come across a page that is larger than the one recorded in the file
                longestPageFile.truncate(0) # Empty the file of its present contents
                longestPageFile.write(url + "`" + str(len(textList))) # Record this page instead
            
            tokenFile.write(" ".join([x for x in nltk.word_tokenize(webpageText) if re.match(r"^[a-zA-Z-]+$|^[a-zA-Z-]+\'[a-zA-Z]+$", x)])) # Writing all words from this page to our token file. Tokenized using the nltk tokenizer (NLTK Project, 2024) while inputting the text that we receive from the webpage through BeautifulSoup() (Richardson, 2025). Added to the file by combining tokens into single string with join() method. Using regular expression matching (Python Software Foundation, 2025a) to ensure that only alphabetical characters and some delimiters (e.g. dashes, apostrophes) are considered tokens to be tokenized later.
    
            visited = [line.rstrip() for line in linkFile] # Put all of the links we have visited into a list so we can easily check if we have visited it in our crawl previously or not.
            
            for link in hyperlinksList: # Cycle through all the hyperlinks we have found on the page
                newURL = link.get('href').lower().strip() # Retrieve the link from the `a` tag which is stored in the `href` tag using `link.get('href')` command (Richardson, 2025). Remove front and back whitespace and lowercase the string representation of the URL afterwards.
    
                if is_valid(newURL): # Check if the URL is valid to be scraped at all
    
                    # re.sub() method used below from (Python Software Foundation, 2025a).
                    url_check = re.sub(r'www\.', "", newURL) # Remove the leading `www.` from the URL.
                    url_check = re.sub(r'https://', "", url_check) # Remove the leading `https://`.
                    url_check = re.sub(r'http://', "", url_check) # Remove the leading `http://`.
                    url_check = re.sub(r'#.+', "", url_check) # Remove the fragment from the URL.
                    url_check = re.sub(r'/+$', "", url_check) # Remove the trailing slashes from the URL.
                    
                    if url_check not in visited: # If the URL has not been visited before (would otherwise create an infinite loop and a trap)
                        
                        linkSet.add(newURL) # Add this URL in its full format to the frontier (it needs the schemes and attachments still because it will be run in is_valid() when it is evaluated)
                        
                        visited.append(url_check) # Add this visited page to the list so that we can prevent traps involving loops to this page
                        linkFile.write(url_check + '\n') # Write the new link to the visited pages txt file with a newline for separation
    
        return list(linkSet) # Return a list of links that will be added to the frontier of the scraper

    except: # If any error occurs, then return empty list to prevent adding to frontier on this URL
        return []

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url) # Functionality and attributes of the parsed object used here and below from (Python Software Foundation, 2025b).
        
        if parsed.scheme not in set(["http", "https"]):
            return False
        
        if not (re.search(r"^(ics|cs|informatics|stat)\.uci\.edu", parsed.netloc.lower().strip()) or re.search(r"\.(ics|cs|informatics|stat)\.uci\.edu", parsed.netloc.lower().strip())): # Check if the URL domain region either starts with `(ics|cs|informatics|stat).uci.edu` or contains a dot before these required subdomains in the format `.(ics|cs|informatics|stat).uci.edu`. re.search() method from (Python Software Foundation, 2025a).
            return False

        if (re.search(r"(page|tag|day|date|week|month|event|filter|feed|comment|download|upname|action|login|logout|edit|page_id=|attachment|redirect|type)", parsed.path.lower().strip() + parsed.query.lower().strip())): # If we find any of these words in the path region or query region of the URL, then declare the entire URL invalid. After some trial and error, we have found that these keywords are most often associated with calendar pages, comment sections, unauthorized downloads, unnecessary attachments, redirects, high quantities of search filter combinations, and other associated traps. re.search() method from (Python Software Foundation, 2025a).
            return False

        # Undesirable file paths that will be invalid if found at the end of a query. Included some other paths we found not given in base code. re.match() method from (Python Software Foundation, 2025a).
        if re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz|bib|py|pps|ppsx|nb|java|heic|ipynb|odc)$", parsed.query.lower().strip()):
                return False

        # Undesirable file paths that will be invalid if found at the end of a path. Included some other paths we found not given in base code. re.match() method from (Python Software Foundation, 2025a).
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz|bib|py|pps|ppsx|nb|java|heic|ipynb|odc)$", parsed.path.lower().strip())

    except TypeError:
        print ("TypeError for ", parsed)
        raise


# Reference(s):
# NLTK Project (2024). nltk.tokenize. NLTK. https://www.nltk.org/_modules/nltk/tokenize.html
# Richardson, L. (2025). Beautiful Soup Documentation. Crummy. https://www.crummy.com/software/BeautifulSoup/bs4/doc/
# Python Software Foundation (2025a). re — Regular expression operations. Python. https://docs.python.org/3/library/re.html
# Python Software Foundation (2025b). urllib.parse — Parse URLs into components. Python. https://docs.python.org/3/library/urllib.parse.html
