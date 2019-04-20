# -*- coding: utf-8 -*-
from __future__ import absolute_import
import re
import csv
#from similarity.cosine import Cosine
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule


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


class WhitepageSpider(CrawlSpider):
    name = 'whitepage'
    allowed_domains = ['whitepages.com.au']
    #start_urls = ['http://whitepages.com.au/']
    start_urls = get_urls('list_one.csv')
    #print(start_urls)
    rules = (
        Rule(LinkExtractor(allow=r'(.*)'), callback='parse_item', follow=False),
    )

    def parse_item(self, response):
        pattern = r'https://www.whitepages.com.au/residential/results?name=(.*)&location=(.*), (.*)&address=(.*)'
        query = re.match(pattern, response.request.url)
        xpath_pattern = '//*[@id="__layout"]/div/main/div/div[2]/div[1]/div/div[2]/div/div/div[1]/a'
        candidates = response.xpath(xpath_pattern)
        print(candidates)
        try:
            for i in response.xpath(xpath_pattern):
                item = {}
                link = candidates.xpath('./@href').get().strip()
                address = candidates.xpath('./div[2]/div[2]/span/text()').get().strip()
                p0 = word2vec(address)
                p1 = word2vec(query.group(5) + ' ' + query.group(3) + ', ' + query.group(4))
                similarity = cosdis(p0, p1)
                if(similarity > 0.5):
                    item['url'] = link
                    item['similarity'] = similarity
                    yield item
                else:
                    item['url'] = link
                    item['similarity'] = similarity
                    yield item
        except:
            pass

