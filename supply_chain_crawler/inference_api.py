import json
import requests
from time import sleep


class InferenceAPI:
    def __init__(self):
        api_token = "api_HEtcUvCvjXPLClCVJbaEwhaqbBmGoDYxFu"
        self.headers = {"Authorization": f"Bearer {api_token}"}
        self.base_url = "https://api-inference.huggingface.co/models/{}"
        self.models = {
            'qna_model': ['deepset/roberta-base-squad2',
                          'deepset/bert-base-cased-squad2',
                          # 'twmkn9/bert-base-uncased-squad2', # remove
                          'deepset/xlm-roberta-large-squad2',
                          # 'deepset/roberta-base-squad2-covid', # remove
                          'ahotrod/electra_large_discriminator_squad2_512'],
            'summary_model': ['sshleifer/distilbart-cnn-12-6',
                              'facebook/bart-large-cnn']
        }

    # ----------------------------------------------------------------------------------------------

    def query(self, payload, model_id):
        API_URL = self.base_url.format(model_id)
        response = requests.post(
            API_URL, headers=self.headers, json=payload).json()
        if isinstance(response, list):
            response = response[0]

        error = response.get('error', None)
        if error is None:
            return response
        else:
            print(response)
            sleep(response['estimated_time'])
            return self.query(payload, model_id)

    # ----------------------------------------------------------------------------------------------

    def summary(self, text, model_id=0):
        model = self.models['summary_model'][model_id]
        response = self.query(payload=text, model_id=model)
        return response['summary_text']

    # ----------------------------------------------------------------------------------------------

    def qna(self, context, question, replace_words):

        answer = []
        question = [question]

        for case in replace_words:
            variation = question[0].replace(case[0], case[1])
            if variation not in question:
                question.append(variation)

        for ques in question:
            for model_id in self.models['qna_model']:

                payload = {
                    'question': ques,
                    'context': context
                }

                response = self.query(payload, model_id)

                start = context[response['start']::-1].find('.')
                end = context[response['end']:].find('.')

                if start == -1:
                    start = 0
                else:
                    start = response['start'] - start + 1

                if end == -1:
                    end = len(context)
                else:
                    end = response['end'] + end + 1

                text = context[start:end].strip()
                if len(text) > 1 and text not in answer:
                    answer.append(text)

            return self.summary(' '.join(answer))

    # ----------------------------------------------------------------------------------------------


# inf_api = InferenceAPI()
# items = json.load(open(r'supply_chain_crawler\results.json'))[0]
#
# context = ' '.join([inf_api.summary(text) for text in items['Summary']])
# question_list = ['What company does?',
#                  'Which Industry is company in?',
#                  'What are the products or services, company offers?',
#                  'What Quality Certifications it has?',
#                  'Who are its current customers?']
#
# # company_name = 'Palletways'
# company_name = 'Wincanton'
# replace_words = [(' company ', ' {company_name} '),
#                  (' it ', ' {company_name} '),
#                  (' its ', ' {company_name} ')]
#
# for answer in inf_api.qna(context=context,
#                           question_list=question_list,
#                           replace_words=replace_words):
#     print(answer, end='\n\n')
