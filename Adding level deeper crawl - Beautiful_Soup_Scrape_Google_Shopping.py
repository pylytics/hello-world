import requests
from bs4 import BeautifulSoup
from io import StringIO
import csv
import urllib
import datetime

#-------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------

inputfile = {}
curr_row = []
row_num = 0
with open('POC SKU and product Names.csv', newline='') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
    for row in spamreader:
        this_row = ', '.join(row)
        product_name_end = this_row.find(',')
        product_name = this_row[0:product_name_end]
        #print(product_name)
        part_number = this_row[product_name_end+2:]
        #print(part_number)
        #print(this_row)
        curr_row.append(product_name)
        curr_row.append(part_number)
        inputfile[row_num] = curr_row
        row_num += 1
        curr_row = []

"""
partnumber = 'UV10157SV'
modifiedproductname = 'Covercraft+UVS100+Windshield+Sun+Shade'

partnumber = 'VW320-08NN'
product_name = 'CalTrend NeoSupreme Seat Covers'
modifiedproductname = product_name.replace(" ","+")

partnumber = input("Enter Part Number: ")
product_name = input("Enter Product Name: ")
modifiedproductname = product_name.replace(" ","+")
""" 

#-------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------

BASE_URL = 'https://www.google.com/search?q={PartNumber}+{ModifiedProductName}&tbm=shop'

hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Referer': 'https://cssspritegenerator.com',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}


all_pages = []
all_listings = {}

#-------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------

def getListings(partnumber, modifiedproductname, start_row):

    row_index = start_row
    this_listing = []
    cols = 0
    
    url = BASE_URL.format(PartNumber=partnumber, ModifiedProductName=modifiedproductname)
    #d = requests.get(url, headers=hdr)

    try:
        d = requests.get(url, headers=hdr)
    except requests.exceptions.RequestException as e:  # This is the correct syntax
        d = str(e)
    #if the URL "get" response was not an exception, continue as usual:
    if type(d) != str:
        soup = BeautifulSoup(d.content, 'html.parser')

        for listing in soup.find_all('div', {'class': 'sh-dlr__content'}):
        #for each listing on the current shopping results page:
            this_listing.append(partnumber)
            this_listing.append(str(modifiedproductname.replace("+"," ")))
            #append part number if found
            if partnumber not in str(listing):
                this_listing.append("PN Not Found")
            else: this_listing.append(partnumber)

            #append the name of the listing
            listing_name = listing.find('div', {'class': '_Tav'})
            listing_name_text = listing_name.text
            listing_name_text = listing_name_text.replace(";","")
            listing_name_text = listing_name_text.replace(",",".")
            this_listing.append(listing_name_text)

            #append the competitor and price
            listing_price = listing.find('div', {'class': '_eUv'})
            for entry in listing_price:
                if "from" in entry.text and len(this_listing) < 5:
                    string = entry.text
                    end = string.find('from') - 1
                    price = string[0:end]
                    competitor = string[end+1:]
                    this_listing.append(competitor)
                    this_listing.append(price)
                    #add an "n/a" column placeholder for unknown shipping & tax
                    this_listing.append('n/a')
                    #add another "n/a" column placeholder for unknown total price
                    this_listing.append('n/a')

            #append the competitor link
            div_with_link = listing.find('div', {'class': 'sh-dlr__thumbnail'})
            link_path = div_with_link.find('a')['href']
            listing_link = "https://www.google.com" + link_path
            this_listing.append(listing_link)
        
            #print ("Length of this listing is: " + str(len(this_listing)))
            #print ("done with current listing")
    
            #add information for this listing to the master list
            all_listings[row_index] = this_listing
            row_index += 1

            cols = len(this_listing)
            #clear contents of the listing-specific array
            this_listing = []
            
    #if the URL generated an exception, add a row to the master file stating the exception
    else:
        this_listing.append(url)
        this_listing.append("url threw exception type: " + str(d))
        for count in range(0,7):
            this_listing.append('n/a')
            print("count = " + str(count))
        all_listings[row_index] = this_listing
        row_index += 1
        cols = len(this_listing)
        this_listing = []

    print ("Row index value = " + str(row_index))
    print ("Number of columns = " + str(cols))

    array_dims = (row_index, cols)
        
    #print ("done with all listings on page")
    return array_dims

#-------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------

#loop through the input file, and for each row, parse product name
# and part number, and call the "getListings" function to scrape
# the Google Shopping page. getListings function appends scrape results
# to the "all_listings" dictionary.

curr_row = 0

#-----------------------------------------------------------
#-----------------------------------------------------------
#UPDATE FOR LOOP ITERATOR WHEN DONE TESTING
#-----------------------------------------------------------
#-----------------------------------------------------------
for i in range (1,3): #(1,row_num): #*****************************************
    product_name = inputfile[i][0]
    #print(product_name)
    partnumber = inputfile[i][1]
    #print(partnumber)
    modifiedproductname = product_name.replace(" ","+")
    
    #call function to scrape Google Shopping
    array_dims = getListings(partnumber, modifiedproductname, curr_row)
    #increment counter of the number of product rows in the main "all_listings" array
    curr_row = array_dims[0]
    columns = array_dims[1]
    #print("new value of curr_row variable: " + str(curr_row))
    #print("new value of columns variable: " + str(columns))
    print("done with " + str(i))

total_rows = curr_row


#-------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------

def crawl_deeper_for_generic_listings(start_rows):
#for each listing in the master "all_listings" array,
    #*******************************************************************************
    #for i in range (total_rows):
    for i in range (0,10):
        #FIX THIS WHEN DONE TESTING **********
        #***************************************************************************
        #...if the fourth column, containing listed competitor name,
        #...contains the generic reference to "store(s)",
        if "store" in all_listings[i][4]:
            #create empty array to store detail_listing info & initialize row counter
            detail_listings = []
            row_index = start_rows
            
            url = all_listings[i][8]
            #d = requests.get(url, headers=hdr)

            try:
                d = requests.get(url, headers=hdr)
            except requests.exceptions.RequestException as e:  # This is the correct syntax
                d = str(e)
            #if the URL "get" response was not an exception, continue as usual:
            if type(d) != str:
                soup2 = BeautifulSoup(d.content, 'html.parser')
                detail_page_title = soup2.find('div', {'class': 'prodbar-title'})
                part_number = all_listings[i][0]     
            
                #populate detail_listings array with detail listings associated to
                # ...the current master listing
                for detail_listing in soup2.find_all('tr', {'class': 'os-row'}):
                    #append part number and product name to array
                    detail_listings.append(all_listings[i][0])
                    detail_listings.append(all_listings[i][1])

                    #append part number if it's part of the page title
                    if str(part_number) in detail_page_title.text:
                        detail_listings.append(str(part_number))
                    else: detail_listings.append("PN Not Found")

                    #append page title
                    detail_page_title2 = str(detail_page_title.text).replace(";"," ")
                    detail_listings.append(detail_page_title2)
                                       
                    #get competitor name and append to array
                    detail_listing_name = detail_listing.find('span', {'class': 'os-seller-name-primary'})
                    competitor_name = detail_listing_name.text.replace(";"," ")
                    #print("competitor name = " + competitor_name)
                    detail_listings.append(competitor_name)

                    #get competitor product prices and append
                    detail_listing_prices = detail_listing.find('td', {'class': 'os-price-col'})
                    product_price = detail_listing_prices.find('span', {'class':'_HDu'})
                    shipping_and_tax_desc = detail_listing_prices.find('div', {'class': 'os-total-description'})
                    total_price = detail_listing.find('td', {'class': 'os-total-col'})
                    detail_listings.append(product_price.text)
                    detail_listings.append(shipping_and_tax_desc.text.replace(";"," "))
                    detail_listings.append(total_price.text)

                    #get competitor shopping link
                    shop_button = detail_listing.find('td', {'class': 'os-button-col'})
                    link_path = shop_button.find('a')['href']
                    listing_link = "https://www.google.com" + link_path
                    detail_listings.append(listing_link)

                    #append detail_listings array to master array and increment row counter
                    all_listings[row_index] = detail_listings
                    row_index += 1

                    #print("detail listing = " + detail_listings)
                    
                    cols = len(detail_listings)
                    #clear contents of the listing-specific array
                    detail_listings = []

            #if the URL generated an exception, add a row to the master file stating the exception
            else:
                detail_listings.append(url)
                detail_listings.append("url threw exception type: " + str(d))
                for count in range(0,7):
                    detail_listings.append('n/a')
                    print("count = " + str(count))
                all_listings[row_index] = detail_listings
                row_index += 1
                cols = len(detail_listings)
                detail_listings = []

    print ("Row index value = " + str(row_index))
    print ("Number of columns = " + str(cols))

    array_dims = (row_index, cols)

    #print ("done with all listings on page")
    return array_dims

                


#-------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------

array_dims = crawl_deeper_for_generic_listings(total_rows)

total_rows = array_dims[0]
print("total rows when completed = " + str(total_rows))

#-------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------

#write output to file
header_row = ("Part Number Searched", "Product Name Searched", "Product Name Found",
              "Listing Name", "Listing Competitor", "Product List Price",
              "Shipping and Tax Description", "Total Price", "Listing Link")

today = str(datetime.date.today())

file_name = str(datetime.date.today()) + ".csv"
#file_path = input("Enter File Folder with Path: ") +'\\' + file_name
#file_path = "C:\Users\lpaulsen\Desktop\Python" + '\\' + file_name

print(file_name)
#print(file_path)

with open(file_name, 'w', newline='') as csvfile:
    spamwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    spamwriter.writerow(header_row)
    for i in range (total_rows):
        spamwriter.writerow(all_listings[i])




