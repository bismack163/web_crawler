# -*- coding: utf-8 -*-
import scrapy


class Hao123Spider(scrapy.Spider):
    name = "hao123"
    allowed_domains = ["www.hao123.com"]
    start_urls = (
        'http://www.www.hao123.com/',
    )

    def parse(self, response):
        pass
