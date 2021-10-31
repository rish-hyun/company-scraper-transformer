# company-scraper-transformer
[![](https://img.shields.io/badge/Python-Scrapy-blue)](https://pypi.org/project/Scrapy/)
[![](https://img.shields.io/badge/Python-Transformers-yellow)](https://pypi.org/project/transformers/)
[![](https://img.shields.io/badge/Python-FPDF-green)](https://pypi.org/project/fpdf/)
[![](https://img.shields.io/badge/Python-PyMongo-white)](https://pypi.org/project/pymongo/)

Supply Chain Companies Analysis using _**Scrapy**_ and _**HuggingFace Transformers**_
<hr>

### Process:
* Spider crawls the urls from `self.company_urls` defined in suppy_chain.py
* Company details such as *Name, House No., Status, Type, Address and Industry* are fetched from [find-and-update.company-information](https://find-and-update.company-information.service.gov.uk/)
* Company *reviews* are scraped from [trustpilot](https://www.trustpilot.com/)
* More details such as *Social accounts, Recent NEWS, Quality, Summary, Sectors, Products and Services* of a company is scraped through it's official website. For this, a custon spider is defined.
* Each scraped item is then processed in `SupplyChainCrawlerPipeline` and stored in **MongoDB**
* Before closing the spider, documents are fetched from **MongoDB** and then **HuggingFace** *Summarization and QnA tasks* are applied over the summary.
* Finalized data is updated in **MongoDB** and a **PDF** report is generaed.

Here is the architecture of our process
![architecture](https://github.com/rish-hyun/company-scraper-transformer/blob/main/ppt/Frame%203.jpg)
<hr>

### HuggingFace Models
Following models are used for **Summarization** task:

```python
'summary_model': [
         'sshleifer/distilbart-cnn-12-6',
         'facebook/bart-large-cnn'
         ]
```

Following models are used for **QnA** task:

```python
'qna_model': [
         'deepset/roberta-base-squad2',
         'deepset/bert-base-cased-squad2',
         'deepset/xlm-roberta-large-squad2',
         'ahotrod/electra_large_discriminator_squad2_512'
         ]
```
<hr>

### Challenges
Following are the challenges I accomplished during the process:

1. HuggingFace QnA models gives answer in few word
    * For this, I summarized the whole data and broke it into several paragraph
    * Applied existing QnA models on summarized text and extracted the line where answer is presen
    * Finally, joined the answers and we got paragraph summarizing all the key points

2. Setting up Pipelines with MongoDB an Transformers
    * Models were taking too much space and time to load. So, I used [huggingface-inference-api](https://huggingface.co/inference-api)
    * Using `PyMongo` locally was not a good idea in long run, so I set up on cloud using **MongoAtlas**
    * Therefore, time and space were reduced in Pipeline

3. Exporting report in a PDF
    * There is no pre-defined function/library in `FPDF` to export **DataFrame or Dict**, so I manually coded from scratch and it worked!
