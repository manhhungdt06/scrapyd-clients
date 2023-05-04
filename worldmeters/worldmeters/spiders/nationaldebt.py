import scrapy
import logging
from scrapy_playwright.page import PageMethod

URL = 'https://worldpopulationreview.com/country-rankings/countries-by-national-debt'
IGNORES = (
    'cds.connatix.com', 'lockerdome',
    'googleapis', 'googleapis', 'amazonaws',
    'googletagmanager', 'quantcast',
)


def should_abort_request(req):
    for item in IGNORES:
        if item in req.url:
            return True

    if req.resource_type == "image" or req.resource_type == "fetch" \
            or req.resource_type == "xhr" or req.resource_type == "stylesheet" \
            or req.resource_type == "other":
        # logging.log(logging.INFO, f"Ignoring {req.url}")
        return True

    if req.method.lower() == 'post':
        # logging.log(logging.INFO, f"Ignoring {req.method} {req.url} ")
        return True

    return False


class NationaldebtSpider(scrapy.Spider):
    name = 'nationaldebt'
    custom_settings = {
        'PLAYWRIGHT_ABORT_REQUEST': should_abort_request,
        'PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT': '100000'
    }

    def start_requests(self):
        yield scrapy.Request(URL, meta={
            'playwright': True,
            'playwright_include_page': True,
            'playwright_page_methods': [PageMethod('wait_for_selector', 'tbody')],
            'errback': self.errback,
        })

    async def parse(self, resp):
        page = resp.meta["playwright_page"]
        await page.close()

        for i, row in enumerate(resp.xpath("//*[contains(@class, 'tp-table-body')]/tbody/tr")):
            # if i == 5:
            #     break
            data = {
                'ratio': row.xpath("td[2]/text()").get(),
                'population': row.xpath("td[3]/text()").get(),
            }
            rqurl = resp.urljoin(row.xpath("td[1]/a/@href").get())
            yield scrapy.Request(url=rqurl, callback=self.parse_detail, meta={'data': data})

    async def parse_detail(self, resp):
        # print(resp.url)
        # example get Population Clock
        COMMON = "(//*[contains(text(), 'Population Clock')])[1]"
        name = resp.xpath(f"{COMMON}/text()").get()

        temp = dict()
        for row in resp.xpath(f"{COMMON}/following-sibling::table/tbody/tr"):
            key = row.xpath("td[1]/text()").get()
            value = row.xpath("td[2]/text()").get()
            temp.setdefault(key, value)

        yield {
            name: temp
        }

    async def errback(self, failure):
        page = failure.request.meta["playwright_page"]
        await page.close()
