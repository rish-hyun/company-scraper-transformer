# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from pymongo import MongoClient
from itemadapter import ItemAdapter
from supply_chain_crawler.inference_api import InferenceAPI
from supply_chain_crawler.export_to_pdf import ExportToPDF


def string_formatter(string):
    is_remain = True
    test_cases = [('–', '-'),
                  ('‘', "'"),
                  ('’', "'"),
                  ('“', "'"),
                  ('”', "'"),
                  ('"', "'"),
                  ('\r', ''),
                  ('\n', ' '),
                  (' .', '.'),
                  ('  ', ' '),
                  ('\u00a0', ' '),
                  ('\u2022', '-')]

    while is_remain:
        for case in test_cases:
            string = string.replace(case[0], case[1])
        for case in test_cases:
            if string.find(case[0]) != -1:
                break
        else:
            is_remain = False
    return string


class SupplyChainCrawlerPipeline:

    def __init__(self) -> None:
        self.db = self.get_database("CompanyDB")['company']
        self.db_ids = [res['ID'] for res in self.db.find()]

    # ----------------------------------------------------------------------------------------------

    def get_database(self, DB_NAME):
        USERNAME = 'xxxxxxxx'
        PASSWORD = 'xxxxxxxx'
        CLUSTER_URL = 'xxxxxxx-xxxxxx.xxxxxx.mongodb.net'

        # Provide the mongodb atlas url to connect python to mongodb using pymongo
        CONNECTION_STRING = f"mongodb+srv://{USERNAME}:{PASSWORD}@{CLUSTER_URL}/{DB_NAME}"

        # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
        return MongoClient(CONNECTION_STRING)[DB_NAME]

    # ----------------------------------------------------------------------------------------------

    def process_item(self, item, spider):
        print('--------------------------------------------------------------')
        for key, val in item.items():

            if val is not None:

                if key == 'Industry':
                    val = val.split('-')[1]

                if type(val) == list:

                    # if key == 'Summary':
                    data_holder = []
                    for text in val:
                        if type(text) == list:
                            text = ' '.join(text)
                        data_holder.append(string_formatter(text))
                    item[key] = data_holder

                else:
                    if type(val) != bool:
                        item[key] = string_formatter(val)

        if item['ID'] not in self.db_ids:
            print(self.db.insert_one(item.copy()))
        return item

    # ----------------------------------------------------------------------------------------------

    def close_spider(self, spider):
        inf_api = InferenceAPI()
        query = {
            'content': True,
            'transform': False
        }

        question_list = ['What company does?',
                         'Which Industry is company in?',
                         'What are the products or services, company offers?',
                         'What Quality Certifications it has?',
                         'Who are its current customers?']

        for doc in self.db.find(query):
            context = ' '.join([inf_api.summary(text)
                                for text in doc['Summary']])
            company_name = doc['Company Name']
            replace_words = [(' company ', f' {company_name} '),
                             (' it ', f' {company_name} '),
                             (' its ', f' {company_name} ')]

            answer = []
            for question in question_list:
                ans = inf_api.qna(context=context, question=question, replace_words=replace_words)
                answer.append(f'{question}\n{ans}')

            doc['Summary'] = answer

            query = {
                "ID": doc['ID']
            }
            update_values = {
                "$set": {
                    "Summary": doc['Summary'],
                    "transform": True
                }
            }
            print(self.db.update_one(query, update_values))
            ExportToPDF().export_to_pdf(doc)

    # ----------------------------------------------------------------------------------------------
