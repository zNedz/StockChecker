import scrapy
import time
import smtplib
from scrapy.loader import ItemLoader
#from ..items import ScrapyItem
from Scrapy.Scrapy.items import ScrapyItem
from scrapy.loader.processors import processors
from scrapy.crawler import CrawlerProcess

from twisted.internet import reactor
from twisted.internet.task import deferLater
from re import sub
from decimal import Decimal


def sendSMS(message):
    sender = "becocciad@gmail.com"
    recievers = ["8285454475@vtext.com", "8282160558@vtext.com"]
    smtpObj = smtplib.SMTP("smtp.gmail.com", 587)
    smtpObj.starttls()
    smtpObj.login(sender, "Fishtank77")
    smtpObj.sendmail(sender, recievers, message)
    smtpObj.quit()



class DataSpider(scrapy.Spider):
    name = "newegg"
    stockList = dict()
    count = 0

    def start_requests(self):
        urls = [
            'https://www.bestbuy.com/site/amd-ryzen-9-5950x-4th-gen-16-core-32-threads-unlocked-desktop-processor-without-cooler/6438941.p?skuId=6438941'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)


    def parse(self, response):
        l = ItemLoader(ScrapyItem(), response)

        l.add_xpath('name', "//*[@id='shop-product-title-f17a6b51-b099-4b71-a6da-d9f19b1a005c']/div/div/div[1]/h1//text()")

        stockInfo = response.xpath("//button[@class='btn btn-primary btn-lg btn-block btn-leading-ficon add-to-cart-button']").get()
        print(stockInfo)
        correctInfo = ""
        bool = False
        if stockInfo is None:
            correctInfo = "Out of Stock"
        else:
            bool = True
            correctInfo = "IN STOCK!!!!!!!!!!!!!!!!!!!"
        l.add_value('stock', correctInfo)
        l.add_value('url', response.url)

        item = l.load_item()


        if bool:
            print("This item is in stock:")
            print(str(item.get('name')[0]).strip('\n'))
            print(item.get('url')[0])
            if len(str(item.get('url'))) > 60:
                message = "This item is in stock:\n" + str(item.get('name')[0]).strip() + "\n" + "URL to long"
            else:
                message = "This item is in stock:\n" + str(item.get('name')[0]).strip() + "\n" + str(item.get('url')[0]).strip()
            #sendSMS(message)
            print("Message sent!")
        #return l.load_item()


#if __name__ == "__main__":
process = CrawlerProcess({
    'LOG_LEVEL': 'ERROR'
})

def sleep(self, *args, seconds):
    """Non blocking sleep callback"""
    return deferLater(reactor, seconds, lambda: None)

def crash(failure):
    print("Spider crashed!")
    print(failure.getTraceback())

def recursive(result, spider):
    defered = process.crawl(spider)
    defered.addCallback(lambda results: print("Waiting 5 second for next run!"))
    defered.addErrback(crash)
    defered.addCallback(sleep, seconds=5)
    defered.addCallback(recursive, spider)


recursive(None, DataSpider)
process.start()

