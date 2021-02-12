import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from dbs.items import Article


class Dbs_spiderSpider(scrapy.Spider):
    name = 'dbs_spider'
    start_urls = ['https://www.dbs.com/media/news-list.page']

    def parse(self, response):
        articles = response.xpath('//div[@id="newsLists"]//ul/li')
        for article in articles:
            link = article.xpath('./a/@href').get()
            date = article.xpath('.//span[@class="news-date"]/text()').get()
            yield response.follow(link, self.parse_article, cb_kwargs=dict(date=date))

    def parse_article(self, response, date):
        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get()
        if title:
            title = title.strip()

        date = datetime.strptime(date.strip(), '%d %b %Y')
        date = date.strftime('%Y/%m/%d')

        content = response.xpath('//div[@class="rich-text-box"]/div//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
