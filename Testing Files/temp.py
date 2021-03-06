from bs4 import BeautifulSoup
import requests

HEADERS = ({'User-Agent':
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
            'Accept-Language': 'en-US, en;q=0.5'})


def amazon_getSearchResult(product_name):
    url = 'https://www.amazon.com/s?k=' + product_name.replace(' ', '+')
    webpage = requests.get(url, headers = HEADERS)
    soup = BeautifulSoup(webpage.content, "lxml")
    links = soup.find_all("a", attrs={'class':'a-link-normal s-no-outline'})
    product_list = []
    for link in links: 
        link = "https://www.amazon.com" + link.get('href')
        print(link)
        product_list.append(amazon_product(link))
        break
    return product_list

def amazon_product(url):
    webpage = requests.get(url, headers=HEADERS)

    soup = BeautifulSoup(webpage.content, "lxml")
    
    title = soup.find("span", attrs={"id":'productTitle'}).text.replace('\n', '').replace('\'', '')
    price = get_price(soup)
    rating = get_rating(soup)
    return [title, price, rating]

def get_price(soup):
    try:
        price = soup.find("span", attrs={'id':'priceblock_ourprice'}).string.strip()
    except AttributeError:
        price = ""  
    return price

def get_rating(soup):
    try:
        rating = soup.find("i", attrs={'class':'a-icon a-icon-star a-star-4-5'}).string.strip()
    except AttributeError:
        try:
            rating = soup.find("span", attrs={'class':'a-icon-alt'}).string.strip()
        except:
            rating = ""
    return rating


print(amazon_getSearchResult('shoes'))