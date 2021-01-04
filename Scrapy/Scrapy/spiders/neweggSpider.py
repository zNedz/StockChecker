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
            'https://www.newegg.com/amd-ryzen-9-5950x/p/N82E16819113663?Description=5950x&cm_re=5950x-_-19-113-663-_-Product',
            'https://www.newegg.com/asus-geforce-rtx-3090-rog-strix-rtx3090-o24g-gaming/p/N82E16814126456?Description=3090&cm_re=3090-_-14-126-456-_-Product',
            'https://www.newegg.com/msi-geforce-rtx-3090-rtx3090-suprim-x-24g/p/N82E16814137610?Description=3090&cm_re=3090-_-14-137-610-_-Product'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)


    def parse(self, response):
        l = ItemLoader(ScrapyItem(), response)

        l.add_xpath('name', "//h1[@class='product-title']//text()")

        stockInfo = response.xpath("//button[@class='btn btn-primary btn-wide']//text()").get()
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
            print(item.get('name'))
            print(item.get('url'))
            message = "This item is in stock:\n" + str(item.get('name')) + "\n" + str(item.get('url'))
            sendSMS(message)
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

