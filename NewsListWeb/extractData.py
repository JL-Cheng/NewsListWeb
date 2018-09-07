# -*- coding:utf-8 -*-

from bs4 import BeautifulSoup
import requests
import threading

class extractData(object):

	def __init__(self,url):
		self.pages=[]
		self.url=url
		self.links=[]
		self.threads=[]

	'''
    获取十条链接
	'''
	def get_10_links(self):
		#获取网页内容
		r=requests.get(self.url)
		soup=BeautifulSoup(r.text,"html.parser")
		#获取10条链接
		number=0
		for tag in soup.find_all('a',attrs={'target':'_blank'}):
			if ('pic' in tag.attrs.get('class',[]) and
				tag.attrs['href'].find('?id')==-1 and
				tag.attrs['href'].find('html')!=-1):
				self.links.append(tag.attrs['href'])
				number=number+1
			if number>=10:
				break
		return self.links

	'''
    处理每个网页的内容
    '''
	def operate_one_page(self,url):
		print(url)
        #获取网页内容
		r=requests.get(url)
		soup=BeautifulSoup(r.text,"html.parser")
        #处理网页内容
		body=soup.body

		page={}
		page['source']=self.url
		page['url']=url
		page['image_url']=''
		page['title']=''
		page['content']=''

		for tag in body.descendants:
            #标题
			if tag.name=='h1':
				page['title']=tag.string.strip()
			#正文
			elif tag.name=='div' and 'content-article' in tag.attrs.get('class',[]):
				for _tag in tag.descendants:
					if (_tag.name=='p' and
						'one-p' in _tag.attrs.get('class',[]) and
                        _tag.string):
						page['content']=page['content']+'&emsp;&emsp;'+_tag.string.strip()+'<br>'
					if (_tag.name=='img' and
						'content-picture' in _tag.attrs.get('class',[])):
						page['image_url']=_tag.attrs['src']
					continue
            #其他
			else:
				continue

		self.pages.append(page)
		return

	'''
    多线程处理网页
    '''
	def multithreading_operate_pages(self):
		self.get_10_links()
		for link in self.links:
			thread=threading.Thread(target=self.operate_one_page,args=(link,))
			self.threads.append(thread)

		for thread in self.threads:
            #开启线程
			thread.start()

		for thread in self.threads:
            #等待线程结束
			thread.join()
		return

if __name__=='__main__':
    test=extractData('http://news.qq.com/')
    test.multithreading_operate_pages()

    print(test.pages)
