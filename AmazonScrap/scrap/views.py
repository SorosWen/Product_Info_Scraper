from django.shortcuts import render
from django.http import HttpResponse
from bs4 import BeautifulSoup, SoupStrainer
import requests

HEADERS = ({'User-Agent':
            'Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36', 
            'Accept-Language': 'en-US, en;q=0.5'})
headers = {
    'authority': 'www.amazon.com',
    'pragma': 'no-cache',
    'cache-control': 'no-cache',
    'dnt': '1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'sec-fetch-site': 'none',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-dest': 'document',
    'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
}

product_number = 12

def interface(request):
    if request.method == 'POST':
        product_name = request.POST['product_name']
        amazon_list = amazon_getSearchResult(product_name)
        ebay_list = ebay_getSearchResult(product_name)
        #recommend_list = getRecommendation(amazon_list + ebay_list)
        return render(request, 'products.html', {'product_name': product_name, 'amazon_list':amazon_list, 'ebay_list': ebay_list})
    else:
        return render(request, 'products.html')


##########################################################
# Recommend Result #######################################
##########################################################
#def getRecommendation(amazon_list):

##########################################################
# Amazon Product Result ##################################
# [url, title, price, rating, review]#####################
##########################################################
def amazon_getSearchResult(product_name):
    url = 'https://www.amazon.com/s?k=' + product_name.replace(' ', '+') + '&ref=nb_sb_noss_1'
    webpage = requests.get(url, headers = headers)
    soup = BeautifulSoup(webpage.content, "lxml", parse_only=SoupStrainer("a", {'class':'a-link-normal s-no-outline'}))
    links = soup.find_all("a", attrs={'class':'a-link-normal s-no-outline'})[0:15]
    product_list = []
    count = product_number
    for link in links: 
        link = "https://www.amazon.com" + link.get('href')
        product_list.append(amazon_product(link))
        if (count <= 0):
            break
        else: 
            count -= 1
    if not product_list:
        print("\nWARNING: The user agent might have been temporarily banned. Please replace the HEADERS with a valid one, or try again later.\n")
        product_list = [["https://developers.whatismybrowser.com", "Empty", "Empty", "Empty"]]
    return product_list

def amazon_product(url):
    webpage = requests.get(url, headers=headers)
    soup = BeautifulSoup(webpage.content, "lxml", parse_only=SoupStrainer(["span", "title"]))
    title = get_title(soup)
    price = get_price(soup)
    rating = get_rating(soup)
    review = get_reviewNum(soup)
    return [str(url), title, price, rating, review]

def get_title(soup):
    try: 
        title = soup.find("span", attrs={"id":'productTitle'}).text.replace('\n', '').replace('\'', '')
    except: 
        try: 
            title = soup.find("span", attrs={"class": 'a-size-large qa-title-text'}).text.replace('\n', '').replace('\'', '')
        except: 
            try: 
                title = soup.title.string.replace('Amazon.com', '')
            except:
                title = "N/A"
    return title

def get_price(soup):
    try:
        price = soup.find("span", attrs={'id':'priceblock_ourprice'}).string.strip()
    except:
        try: 
            price = soup.find("span", attrs={'class': 'a-offscreen'}).string
        except: 
            price = "N/A"
    return price

def get_rating(soup):
    try:
        rating = soup.find("span", attrs={'class':'a-icon-alt'}).string.strip()
    except:
        rating = ""
    return rating

def get_reviewNum(soup): 
    try:
        review = soup.find("span", attrs={'id':'acrCustomerReviewText'}).string.strip()
    except:
        review = ""
    return review

##########################################################
# eBay Product Result ###################################
##########################################################
def ebay_getSearchResult(product_name):
    url = 'https://www.ebay.com/sch/i.html?_from=R40&_trksid=p2380057.m570&_nkw=' + product_name.replace(' ', '+') + '&_sacat=0'
    webpage = requests.get(url, headers = HEADERS)
    soup = BeautifulSoup(webpage.content, "lxml", parse_only=SoupStrainer("a", {'class':'s-item__link'}))
    links = soup.find_all("a", attrs={'class':'s-item__link'})[0: 15]
    product_list = []
    count = product_number
    for link in links: 
        link = link.get('href')
        product_list.append(ebay_product(link))
        if count <= 0:
            break
        else:
            count -= 1
    return product_list

def ebay_product(url):
    webpage = requests.get(url)
    soup = BeautifulSoup(webpage.text, "html.parser", parse_only=SoupStrainer(["title", "span", "div"]))
    title = ebay_get_title(soup)
    price = ebay_get_price(soup)
    condition = ebay_get_condition(soup)
    return [str(url), title, price, condition]

def ebay_get_title(soup):
    try: 
        title = soup.title.string.replace('  | eBay', '')
    except:
        title = "N/A"
    return title

def ebay_get_price(soup):
    try:
        price = soup.find("span", attrs={'id':'prcIsum'}).string.replace('US ', '').replace('/ea', '').strip()
    except: 
        try:
            price = soup.find("span", attrs={'class':'notranslate', 'itemprop':'price'}).string.replace('US', '').replace(' ', '').strip()
        except:
            price = "N/A"
    return price

def ebay_get_condition(soup):
    try:
        condition = soup.find("div", attrs={'id':'vi-itm-cond'}).text
    except:
        condition = "N/A"
    return condition
