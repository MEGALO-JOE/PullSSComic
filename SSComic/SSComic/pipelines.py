# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


import pymongo
from scrapy.exporters import JsonItemExporter


class SscomicPipeline(object):
    def process_item(self, item, spider):
        return item


class ProxyMiddleware(object):
    def process_request(self, request, spider):
        # proxies可以在settings.py中，也可以来源于代理ip的webapi，也可以从代理ip池中获取
        # proxy = random.choice(proxies)
        # 免费的会失效
        proxy = 'https://1.71.188.37:3128'
        request.meta['proxy'] = proxy


# class SscomicJsonPipeline(object):
#     # 在爬虫启动时，调用一次
#     def open_spider(self, spider):
#         # print(spider.name)
#         self.file = open("./death.json", "w")
#
#     # 引擎将spider返回的item对象，交给了管道的 process_item方法进行存储处理。
#     def process_item(self, item, spider):
#         item = dict(item)
#         item.pop("image_file")
#         json_str = json.dumps(item, ensure_ascii=False, indent=4) + ",\n"
#         self.file.write(json_str)
#
#         return item
#
#     # 在爬虫结束时，调用一次
#     def close_spider(self, spider):
#         self.file.close()


class SscomicJsonPipeline(object):
    def open_spider(self, spider):
        # 可选实现，当spider被开启时，这个方法被调用。
        # 输出到tongcheng_pipeline.json文件
        self.file = open('item.json', 'wb')
        self.exporter = JsonItemExporter(self.file, encoding='utf-8')
        self.exporter.start_exporting()

    def close_spier(self, spider):
        # 可选实现，当spider被关闭时，这个方法被调用
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        item.__delitem__("image_file")
        self.exporter.export_item(item)
        return item


class ItcastMongoPipeline(object):
    def open_spider(self, spider):
        self.teacher = pymongo.MongoClient().itcast.teacher

    def process_item(self, item, spider):
        self.teacher.insert(dict(item))
        return item
