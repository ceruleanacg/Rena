# coding=utf-8

from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader

from crawlers.news.items import SibaNewsItem

from datetime import datetime


class SibaNewsSpider(CrawlSpider):

    name = 'siba_news'
    allowed_domains = ['snh48.com']
    start_urls = ['http://www.snh48.com/html/allnews/']

    parse_regex = '(gongyan|woshouhui|cd|zixun|activity)/201[3-6]/(\d){4}/(.)+'
    follow_regex = '(\d)+.html'

    parse_rule = Rule(
        LinkExtractor(allow=[parse_regex]),
        callback='parse_news'
    )

    follow_rule = Rule(
        LinkExtractor(allow=[follow_regex])
    )

    rules = [parse_rule]

    def parse_news(self, response):
        xpaths = response.xpath("//div[contains(@class, 's_new_detail')]")
        target = xpaths[0] if len(xpaths) > 0 else None

        if target:
            news_url = response.url
            news_type = news_url.split('/')[-4]
            news_title = target.xpath(".//div[@class='s_nt_txt']/text()").extract_first()
            news_article = target.xpath(".//div[@class='s_new_con']/div/span/span/text()").extract()
            news_image_urls = target.xpath(".//img[contains(@src, 'newsimg')]/@src").extract()

            news_create_year = news_url.split('/')[-3]
            news_create_month = news_url.split('/')[-2][0:2]
            news_create_day = news_url.split('/')[-2][2:4]

            news_create_date = news_create_year + '-' + news_create_month + '-' + news_create_day + ' ' + '00:00:00'

            news_title = news_title.strip()

            articles = []

            for article in news_article:
                articles.append(article.strip())

            siba_item_loder = ItemLoader(item=SibaNewsItem(), response=response)
            siba_item_loder.add_value('url', news_url)
            siba_item_loder.add_value('type', news_type)
            siba_item_loder.add_value('source', "官网")
            siba_item_loder.add_value('title', news_title)
            siba_item_loder.add_value('article', articles)
            siba_item_loder.add_value('create_date', datetime.strptime(news_create_date, "%Y-%m-%d %H:%M:%S"))
            siba_item_loder.add_value('image_urls', news_image_urls)

            return siba_item_loder.load_item()