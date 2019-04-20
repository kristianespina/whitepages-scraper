# -*- coding: utf-8 -*-
import scrapy
from scrapy.http.request import Request
import re
import csv
from urllib.parse import unquote

def get_urls(filename='list.csv'):
    start_urls = []
    #df = pd.read_csv(filename).values  # Get only useful stuff
    df = []
    with open(filename, 'r') as csvFile:
        reader = csv.reader(csvFile)
        for row in reader:
            df.append(row)

    csvFile.close()
    for i in df:
        start_urls.append('https://www.whitepages.com.au/residential/results?name={}&location={}, {}&address={}'.format(i[1], i[3], i[4], i[2]))
    return start_urls

def word2vec(word):
    from collections import Counter
    from math import sqrt

    # count the characters in word
    cw = Counter(word)
    # precomputes a set of the different characters
    sw = set(cw)
    # precomputes the "length" of the word vector
    lw = sqrt(sum(c*c for c in cw.values()))

    # return a tuple
    return cw, sw, lw

def cosdis(v1, v2):
    # which characters are common to the two words?
    common = v1[1].intersection(v2[1])
    # by definition of cosine distance we have
    return sum(v1[0][ch]*v2[0][ch] for ch in common)/v1[2]/v2[2]


class SmallSpider(scrapy.Spider):
    name = 'small'
    allowed_domains = ['whitepages.com.au']
    start_urls = get_urls('list.csv')

    def parse(self, response):
        pattern = r'name=(.*)&location=(.*), (.*)&address=(.*)'
        query = re.search(pattern, unquote(response.request.url))
        xpath_pattern = '//*[@id="__layout"]/div/main/div/div[2]/div[1]/div/div[2]/div/div/div[1]/a'
        candidates = response.xpath(xpath_pattern)
        try:
            for i in candidates:
                item = {}
                link = 'https://www.whitepages.com.au'+candidates.xpath('./@href').get().strip()
                address = candidates.xpath('./div[2]/div[2]/span/text()').get().strip()
                p0 = word2vec(address)
                p1 = word2vec(query.group(4) + ' ' + query.group(2) + ', ' + query.group(3))
                similarity = cosdis(p0, p1)
                #print('--------- SIMILARTY: {}'.format(similarity))
                if(similarity >= 0.90):
                    item['url'] = link
                    item['name'] = query.group(1)
                    item['address'] = query.group(4)
                    item['suburb'] = query.group(1)
                    item['postcode'] = query.group(3)
                    item['similarity'] = similarity
                    request = Request(link, callback=self.getPhone, meta={'item': item})
                    print(request)
                    yield request
                else:
                    pass
        except:
            pass

    def getPhone(self, response):
        item = response.meta['item']
        print(item)
        try:
            phone_xpath ='//*[@id="__layout"]/div/main/div/div[2]/div[1]/div/div[1]/div[2]/span[2]/a/text()'
            phone = response.xpath(phone_xpath).get()
            item['phone'] = phone
            yield item
        except:
            yield item



