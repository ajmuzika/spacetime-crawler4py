def main():

    visitedLinks = open("visitedLinks.txt", "r") # Open the visited links file
    
    link = visitedLinks.readline() # Read each line
    
    subdomains = dict() # Put each subdomain
    
    while link != "": # While we are still going through the file and have not ended
    
        if ".ics.uci.edu" in link: # If the URL is of the ics.uci.edu domain and has a leading dot for including a subdomain
            
            sub = link.split(".ics.uci.edu")[0].strip() # Get the subdomain part of the URL string
            
            if sub not in subdomains.keys(): # If we have not come across this subdomain before
                subdomains[sub] = 1 # Add it to the dictionary and tally that instance we are processing to its value
            else:
                subdomains[sub] += 1 # Increment for every additiona

        link = visitedLinks.readline() # Read the next line
    
    visitedLinks.close() # Close the file

    subdomainsList = sorted(list(subdomains.keys())) # Sorting the subdomains alphabetically

    for l in subdomainsList: # Print in the prescribed format and ordering from the prompt
        print(f"{l}.ics.uci.edu, {subdomains[l]}")

if __name__ == "__main__":
    main()
