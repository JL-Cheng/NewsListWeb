#-*- coding:utf-8 -*-

from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators import csrf
from NewsModel.models import news
from NewsListWeb.extractData import extractData
from NewsListWeb.searchNews import searchNews

#设置一些全局变量
admin=False
login_input=True

'''
函数功能：用于显示数据库中的新闻与网页状态
返回值：一个dict类型的参数集
'''
def get_context():
    #将新闻内容显示出来
    newsList=news.objects.all()
    page_numbers=len(newsList)
    pages=[]
    for info in newsList:
        data={
            'source':info.source,
            'url':info.url,
            'image_url':info.image_url,
            'title':info.title,
            'content':info.content,
            'show':False,
        }
        pages.append(data)
    context={'pages':pages,'page_numbers':page_numbers,'admin':admin,'login_input':login_input}
    return context

'''
函数功能：
1、爬取最新网页，判重后放入数据库
2、从数据库中读取网页内容并展示
'''
def init(request):
    #全局变量初始化
    global admin,login_input
    admin=False
    login_input=True

    newsList=news.objects.all()
    #爬取网页
    pagesData=extractData('http://news.qq.com/')
    pagesData.multithreading_operate_pages()
    #将不在新爬取结果中的网页删除
    new_titles=[x['title'] for x in pagesData.pages]
    for page in newsList:
        if page.title not in new_titles:
            page.delete()

    newsList=news.objects.all()
    #将新爬取结果添加到数据库
    old_titles=[x.title for x in newsList]
    for page in pagesData.pages:
        if page['title'] not in old_titles:
            data=news(source=page['source'],
                        url=page['url'],
                        image_url=page['image_url'],
                        title=page['title'],
                        content=page['content'])
            data.save()

    context=get_context()
    return render(request,'newslist.html',context)

'''
函数功能：
管理登录界面
'''
def login(request):
    global admin,login_input
    if request.POST:
        #是登入命令
        if 'username' in request.POST.keys():
            username=request.POST['username']
            password=request.POST['password']
            #如果登陆成功
            if (username=='NOIR' and password=='l14240119981031'):
                admin=True
                login_input=True
                context=get_context()
                return render(request,'newslist.html',context)
            #否则如果失败，发出alert警告
            else:
                admin=False
                login_input=False
                context=get_context()
                return render(request,'newslist.html',context)
        #是登出命令
        else:
            admin=False
            login_input=True
            context=get_context()
            return render(request,'newslist.html',context)
    else:
        return HttpResponseRedirect('/')

'''
函数功能：
显示用户希望查看的新闻详情
'''
def show(request):
    #全局变量初始化
    global login_input
    login_input=True
    if request.POST:
        show_title,is_show=request.POST['show_button'].split('+')
        context=get_context()
        for page in context['pages']:
            if page['title']==show_title:
                if is_show=='False':
                    page['show']=True
                break
        return render(request,'newslist.html',context)
    else:
        return HttpResponseRedirect('/')

'''
函数功能：
删除对应的新闻
'''
def delete(request):
    #全局变量初始化
    global login_input
    login_input=True
    if request.POST:
        delete_title=request.POST['delete_button']
        news.objects.filter(title=delete_title).delete()
        context=get_context()
        return render(request,'newslist.html',context)
    else:
        return HttpResponseRedirect('/')

'''
函数功能：
搜索对应的新闻并进行排序
'''
def search(request):
    #全局变量初始化
    global login_input
    login_input=True
    if request.POST:
        search_str=request.POST['search_str']
        if search_str!='':
            search_news=searchNews()
            search_news.search_pages(search_str)
        context=get_context()
        return render(request,'newslist.html',context)
    else:
        return HttpResponseRedirect('/')
