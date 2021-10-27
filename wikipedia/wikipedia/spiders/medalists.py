import scrapy

import os
from os.path import dirname

current_dir = os.path.dirname(__file__)
print(f"current dir: {current_dir}")
top_dir = dirname(dirname(dirname(current_dir)))
print(f"top dir {top_dir}")
url = os.path.join(top_dir, "html/1992_World_Junior_Championships_in_Athletics_–_Men's_high_jump")


class MedalistsSpider(scrapy.Spider):
    name = 'medalists'
    allowed_domains = ['wikipedia.org']
    start_urls = [f"file://{url}"]

    def parse(self, response):
        table = response.xpath('//table')[1].xpath('tbody')
        for tr in table.xpath('tr'):
            print(tr.xpath('td/b/text()').extract()[0],
            tr.xpath('td/a/text()').extract()[0]
        )

