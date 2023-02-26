import requests
from bs4 import BeautifulSoup
from lxml import etree
import pandas as pd
import csv

product_link = []
name_lst = []
price_lst = []
rating_lst = []
review_lst = []
desc_lst = []
asin_lst = []
manufacture_lst = []


def product_name(soup):

    try:
        name = soup.find(
            'span', attrs={"id": "productTitle"}).string.strip()
    except AttributeError:
        name = 'NA'
    return name_lst.append(name)


def product_price(soup):

    try:
        price = soup.find(
            'span', attrs={"class": "a-offscreen"}).string.strip()
    except AttributeError:
        price = 'NA'
    return price_lst.append(price)


def product_rating(soup):
    try:
        ratings = soup.find(
            'span', attrs={"id": "acrCustomerReviewText"}).string.strip().split(" ")[0]
    except AttributeError:
        ratings = 'NA'
    return rating_lst.append(ratings)


def customer_reviews(soup):
    try:
        element = soup.find(
            'a', attrs={"id": "askATFLink"})
        review = element.find('span').string.strip().split(" ")[0]
    except AttributeError:
        review = 'NA'
    return review_lst.append(review)


def description(soup):
    txt = ""
    try:
        element = soup.find(
            'div', attrs={'id': 'feature-bullets'})
        details = element.find_all('span', attrs={'class': 'a-list-item'})

        for detail in details:
            txt += detail.get_text()
    except AttributeError:
        detail = 'NA'
    return desc_lst.append(txt.strip())


def asin_no():
    try:
        split = link.split("dp")
        a = split[1]
        slicing = a[1:13:1]
        modifying1 = slicing.removeprefix("2F")
        modifying2 = modifying1.removesuffix("/r")
    except AttributeError:
        modifying2 = 'NA'
    return asin_lst.append(modifying2)


def manufacture(soup):
    dom = etree.HTML(str(soup))
    h2_xpath = dom.xpath("//*[@id='detailBulletsWrapper_feature_div']/h2")
    h2_lst = []
    for i in h2_xpath:
        h2_lst.append(i.text)
        try:
            element = soup.find(
                "div", attrs={"id": "detailBullets_feature_div"})
            keys = element.find_all("span", attrs={"class": "a-text-bold"})
            list_of_keys = []
            for key in keys:
                list_of_keys.append(key.get_text())

            key_txt = "".join(list_of_keys)
            remove_extra_space = "".join(key_txt.split())
            remove_unicode = remove_extra_space.encode("ascii", "ignore")
            string = remove_unicode.decode()
            list_of_strs = list(string.split(":"))

            # Finding Vals
            xpath_val = dom.xpath(
                "//*[@id='detailBullets_feature_div']/ul/li/span/span[2]")

            vals = []
            for i in xpath_val:
                vals.append(i.text)

            new_dict1 = dict(zip(list_of_strs, vals))
            manufacture1 = new_dict1["Manufacturer"]
        except KeyError:
            manufacture1 = "Not mentioned"
        return manufacture_lst.append(manufacture1)
    else:
        try:
            element2 = soup.find(
                "table", attrs={"id": "productDetails_techSpec_section_1"})
            element2_keys = element2.find_all(
                "th", attrs={"class": "a-color-secondary a-size-base prodDetSectionEntry"})
            element2_vals = element2.find_all(
                "td", attrs={"class": "a-size-base prodDetAttrValue"})

            element2_keys_lst = []
            for i in element2_keys:
                element2_keys_txt = i.get_text()
                key_remove_lspace = element2_keys_txt.lstrip()
                key_remove_rspace = key_remove_lspace.rstrip()
                element2_keys_lst.append(key_remove_rspace)

            element2_vals_lst = []
            for i in element2_vals:
                element2_vals_lst.append(i.get_text())

            lst_of_vals = []
            for i in element2_vals_lst:
                enc = i.encode("ascii", "ignore")
                dec = enc.decode()
                lst_of_vals.append(dec)

            final_list_of_vals = []
            for i in lst_of_vals:
                remove_escape_chr = i.replace("\n", "")
                remove_lspace = remove_escape_chr.lstrip()
                remove_rspace = remove_lspace.rstrip()
                final_list_of_vals.append(remove_rspace)

            dict2 = dict(zip(element2_keys_lst, final_list_of_vals))
            manufacture2 = dict2["Manufacturer"]
        except KeyError:
            manufacture2 = "Not Mentioned"

        return manufacture_lst.append(manufacture2)


def looping_url():
    page = 1
    urls_list = []
    while page != 7:

        url = f"https://www.amazon.in/s?k=bags&page={page}"
        useragent = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'}

        web_page = requests.get(url, headers=useragent)
        web_page.raise_for_status()

        soup = BeautifulSoup(web_page.content, 'html.parser')

        product_urls = soup.find_all("a", attrs={
            "class": "a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal"})

        if product_urls is None:
            raise Exception("URL not found!")

        else:
            for urls in product_urls:
                urls_list.append(urls.get('href'))

            global link
            for link in urls_list:
                new_webpage = requests.get(
                    "https://www.amazon.in" + link, headers=useragent)
                new_soup = BeautifulSoup(new_webpage.content, 'html.parser')

                product_link.append("https://www.amazon.in" + link)
                product_name(new_soup)
                product_price(new_soup)
                product_rating(new_soup)
                customer_reviews(new_soup)
                description(new_soup)
                asin_no()
                manufacture(new_soup)

        page = page + 1


def save_to_csv():
    csv_header = ["URL", "Name", "Price", "Rating",
                  "Review", "Description", "ASIN", "Manufacturer"]
    whole_data = []

    for url, name, price, rating, review, desc, asin, manufacture in zip(product_link, name_lst, price_lst, rating_lst, review_lst, desc_lst, asin_lst, manufacture_lst):
        whole_data.append(url)
        whole_data.append(name)
        whole_data.append(price)
        whole_data.append(rating)
        whole_data.append(review)
        whole_data.append(desc)
        whole_data.append(asin)
        whole_data.append(manufacture)

    nested_list = [whole_data[i:i+8] for i in range(0, len(whole_data), 8)]

    with open("data.csv", "w", encoding="utf-8", newline="") as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(csv_header)
        csv_writer.writerows(nested_list)


if __name__ == "__main__":
    looping_url()
    # print(name_lst)
    # print(price_lst)
    # print(rating_lst)
    # print(review_lst)
    # print(desc_lst)
    # print(asin_lst)
    # print(manufacture_lst)
    save_to_csv()
