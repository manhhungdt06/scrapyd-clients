from scrapy import Spider

class CountriesSpider(Spider):
    name = 'countries'
    start_urls = ['https://www.worldometers.info/world-population/population-by-country/']

    def parse(self, resp):
        for country in resp.xpath("//td/a"):
            yield resp.follow(url=country.xpath(".//@href").get(),
                              callback=self.parse_country,
                              meta={"country_name": country.xpath(".//text()").get()})

    def parse_country(self, resp):
        country_name = resp.request.meta["country_name"]
        temp = dict()
        for row in resp.xpath("//*[contains(@class, 'table-striped')]/tbody/tr"):
            year = row.xpath(".//td[1]/text()").get()
            population = row.xpath(".//td[2]/strong/text()").get()
            temp.setdefault(year, population)
        yield {country_name: temp}
