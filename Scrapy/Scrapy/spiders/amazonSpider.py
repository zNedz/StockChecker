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
            'https://www.amazon.com/AMD-Ryzen-5950X-32-Thread-Processor/dp/B0815Y8J9N/ref=pd_sbs_147_2/146-5748473-7863964?_encoding=UTF8&pd_rd_i=B0815Y8J9N&pd_rd_r=43c9ae6a-70c4-4ca0-9934-2b99779aebe7&pd_rd_w=vsqMv&pd_rd_wg=VtCRH&pf_rd_p=ed1e2146-ecfe-435e-b3b5-d79fa072fd58&pf_rd_r=0CB0KTTTM1T3QQ10PPWH&psc=1&refRID=0CB0KTTTM1T3QQ10PPWH',
            'https://www.amazon.com/Ryzen-5950X-32-Thread-Unlocked-Processor/dp/B08PCF3Z7X/ref=sr_1_1?dchild=1&keywords=5950x&qid=1609719314&sr=8-1'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)


    def parse(self, response):
        l = ItemLoader(ScrapyItem(), response)

        l.add_xpath('name', "//*[@id='productTitle']//text()")
        l.add_xpath('price', "//*[@id='price_inside_buybox']//text()")

        stockInfo = response.xpath("//*[@id='add-to-cart-button']").get()
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
        moneyString = item.get('price')
        moneyValue = 0
        if moneyString is not None:
            #print(moneyString)
            moneyValue = Decimal(sub(r'[^\d.]', '', moneyString[0]))


        if bool and moneyValue < 800:
            print("This item is in stock:")
            print(str(item.get('name')[0]).strip('\n'))
            print(item.get('url')[0])
            print(moneyValue)
            if len(str(item.get('url'))) > 60:
                message = "This item is in stock:\n" + str(item.get('name')[0]).strip() + "\n" + "URL to long"
            else:
                message = "This item is in stock:\n" + str(item.get('name')[0]).strip() + "\n" + str(item.get('url')[0]).strip()
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

