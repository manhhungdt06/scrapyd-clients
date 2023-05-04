# -*- coding: utf-8 -*-
import scrapy

ITEMS = 56


class SpecialSpider(scrapy.Spider):
    name = 'special_offers'
    start_urls = [
        'https://web.archive.org/web/20190225123327/https://www.tinydeal.com/specials.html'
    ]

    def parse(self, resp):
        for product in resp.xpath("//ul[@class='productlisting-ul']/div/li"):
            yield {
                "title": product.xpath(".//a[@class='p_box_title']/text()").get(),
                "url": resp.urljoin(product.xpath(".//a[@href='p_box_title']/@href").get()),
                "discounted_price": product.xpath(".//div[@class='p_box_price']/span[1]/text()").get(),
                "original_price": product.xpath(".//div[@class='p_box_price']/span[2]/text()").get(),
            }

        next_page = resp.xpath("//a[@class='nextPage']/@href").get()
        # print(f"HUNG HUNG next_page: {next_page}")
        if next_page:
            yield scrapy.Request(url=next_page, callback=self.parse)
