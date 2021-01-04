import scrapy


class QuotesSpider(scrapy.Spider):
    name = "quotes"

    def start_requests(self):
        urls = [
            'http://quotes.toscrape.com/page/1/',
            'http://quotes.toscrape.com/page/2/',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)
#/html/body/div/div[2]/div[1]/div[1]/span[1]
    def parse(self, response):
        data = response.xpath("//span[@class='text']").getall()

        for item in data:
            print(item)


