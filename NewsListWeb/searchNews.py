# -*- coding:utf-8 -*-

from functools import reduce
import jieba,json,re,django,sys,os

sys.path.append("..")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "NewsListWeb.settings")
django.setup()
from NewsModel.models import news

class searchNews(object):

    def __init__(self):
        self.data=[]#存储提取的数据
        self.ordered_title=[]#存储排好序的标题
    '''
    进行信息提取与分词的工作
    '''
    def extract_info(self):
        newsList=news.objects.all()
        for page in newsList:
            #用data存储提取的数据
            data={}

            data['title']=page.title

            #使用正则表达式抽取日期
            data['date']=[]
            datePattern=re.compile(r'(?:\d{4}(?:年|\/|\-))?(?:[01]?\d(?:月|\/|\-))(?:[0-3]?\d日?)?')
            date=list(filter(lambda x:len(x)>2,datePattern.findall(page.content)))
            data['date']=data['date']+date

            #使用分词工具进行分词
            data['words']=list(jieba.cut_for_search(page.content))
            #存储原网址
            data['url']=page.url

            self.data.append(data)
        return

    '''
    搜索最相似网页标题,进行排序,返回参数集
    '''
    def search_pages(self,test_str):
        self.extract_info()
        #构造倒排索引
        dictionary={}
        for page in self.data:
            for word in page['words']:
                if word not in dictionary.keys():
                    dictionary[word]={}
                    dictionary[word][page['title']]=1
                else:
                    if page['title'] not in dictionary[word].keys():
                        dictionary[word][page['title']]=1
                    else:
                        dictionary[word][page['title']]=dictionary[word][page['title']]+1
        for word in dictionary.keys():
            dictionary[word]=dict(sorted(dictionary[word].items(),key=lambda item:item[1],reverse=True))

        #进行搜索（先检索日期，再统计词频）
        result={}

        #输入的是日期
        datePattern=re.compile(r'(?:\d{4}(?:年|\/|\-))?(?:[01]?\d(?:月|\/|\-))(?:[0-3]?\d日?)?')
        test_date=list(filter(lambda x:len(x)>2,datePattern.findall(test_str)))
        for date in test_date:
            date=list(filter(lambda x:x!='',re.split(r'[^\d]',date)))
            for page in data:
                for page_date in page['date']:
                    if date==list(filter(lambda x:x!='',re.split(r'[^\d]',page_date))):
                        if page['title'] in result.keys():
                            result[page['title']]=result[page['title']]+10
                        else:
                            result[page['title']]=10
                        break
        #输入的是普通词
        test_words=list(jieba.cut_for_search(test_str))
        for word in test_words:
            if word in dictionary.keys():
                for title in dictionary[word].keys():
                    if title in result.keys():
                        result[title]=result[title]+dictionary[word][title]
                    else:
                        result[title]=dictionary[word][title]
            else:
                continue

        #加入无关标题
        for page in self.data:
            if page['title'] not in result.keys():
                result[page['title']]=0

        self.ordered_title=sorted(result.keys(),key=lambda a:result[a],reverse=True)

        #更新数据库中的排序
        id=max([x.id for x in news.objects.all()])+1
        for title in self.ordered_title:
            info=news.objects.filter(title=title)
            info.update(id=id)
            #info.save()
            id=id+1

        news.objects.order_by("id")
        return


if __name__=='__main__':
    test=searchNews()
    test.search_pages('我有一个梦想')
