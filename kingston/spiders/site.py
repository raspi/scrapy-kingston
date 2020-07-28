import json

import scrapy

from kingston.items import *


class ManufacturerSpider(scrapy.Spider):
    """
    Get all compatible memory for all motherboards from certain manufacturer
    """
    name = 'manufacturer'
    allowed_domains = [
        'kingston.com',
        'www.kingston.com',
    ]
    start_urls = [
        'https://kingston.com/',
    ]

    manufacturer = None

    def __init__(self, manufacturer: str = ""):
        if manufacturer == "":
            manufacturer = None

        if manufacturer is None:
            raise ValueError("Invalid manufacturer given")

        self.manufacturer = manufacturer

        self.start_urls = ['https://www.kingston.com/en']

    def parse(self, response: scrapy.http.Response):
        yield scrapy.FormRequest(
            'https://www.kingston.com/en/memorysearch/ajax/getlines',
            callback=self.POST_parse_models,
            formdata={
                'systemCategoryId': '7',
                'manufacturerId': self.manufacturer,
                'discontinued': 'false',
            },
            meta={
                'manufacturerId': self.manufacturer,
            },
        )

    def POST_parse_models(self, response: scrapy.http.Response):
        for model in json.loads(response.body):
            yield scrapy.FormRequest(
                'https://www.kingston.com/en/memorysearch/ajax/getmodels',
                callback=self.POST_parse_model,
                formdata={
                    'systemCategoryId': '7',
                    'manufacturerId': self.manufacturer,
                    'systemLine': model['Value'],
                    'discontinued': 'false',
                },
                meta={
                    'manufacturerId': self.manufacturer,
                    'systemLine': model['Value'],
                },
            )

    def POST_parse_model(self, response: scrapy.http.Response):
        data = json.loads(response.body)[0]
        yield scrapy.Request(
            f"https://www.kingston.com/en/memory/search?model={data['Value']}&mfr={self.manufacturer}",
            callback=self.parse_memory,
            meta={
                'manufacturerId': self.manufacturer,
                'model': data['Value'],
                'systemLine': response.meta['systemLine'],
            },
        )

    def parse_memory(self, response: scrapy.http.Response):
        """
        Get compatible memory modules
        """

        prodinfo = {}

        for info in response.xpath("//div[@class='c-table__main_disable']/table/tr"):
            k = info.xpath("./td[1]/text()").get().strip()
            v = "".join(info.xpath("./td[2]//text()").getall()).strip()
            prodinfo[k] = v

        compatible_modules = Memory({
            "_url": response.url,
            "_manufacturer": response.meta['manufacturerId'],
            "_model": response.meta['systemLine'],
            "_product": prodinfo,
        })

        for section in response.xpath("//section[contains(@class, 'section-product_gallery')][@id]"):
            title = section.xpath(".//h2/text()").get().strip()
            if "RAM" not in title:
                continue

            compatible_modules[title] = []

            for memmodule in section.xpath("./ul[contains(@class, 'c-productGallery')]/li"):
                name = memmodule.xpath("./@data-pn").get()

                moduleinfo = {
                    "_name": name,
                }

                for infoline in memmodule.xpath(".//div[@class='c-productCard__body__details']/ul/li"):
                    txt = "".join(infoline.xpath(".//text()").getall()).strip()

                    if txt == 'PCN':
                        # Product change notify, ignore
                        continue
                    elif 'Spec Sheet PDF' in txt:
                        moduleinfo[txt] = infoline.xpath(".//a/@href").get()
                    else:
                        if ':' not in txt:
                            continue

                        k, v = txt.split(": ", 1)

                        if 'Specs' in k:
                            v = v.split(", ")

                        moduleinfo[k] = v

                compatible_modules[title].append(moduleinfo)

        yield compatible_modules
