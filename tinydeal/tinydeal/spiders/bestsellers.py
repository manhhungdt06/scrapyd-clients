from scrapy import Spider, Request


class BestsellersSpider(Spider):
    name = 'bestsellers'
    start_urls = ['https://www.glassesshop.com/bestsellers']

    def parse(self, response):
        for product in response.xpath("//*[@id='product-lists']/div"):
            yield {
                "url": product.xpath(".//div[@class='product-img-outer']/a/@href").get(),
                "img_url": product.xpath(".//div[@class='product-img-outer']/a/img/@data-src").getall(),
                "name": product.xpath(".//div[@class='product-img-outer']/a/img[1]/@alt").get(),
                "price": product.xpath(".//div[@class='p-price']/div/span/text()").get(),
            }

        next_page = response.xpath("//a[@class='page-link' and text()='Next']/@href").get()
        if next_page:
            yield Request(url=next_page, callback=self.parse)