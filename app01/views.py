from django.shortcuts import render,HttpResponse,redirect
import json
from app01 import models
from django.contrib.auth import authenticate,login,logout
from Blog_system import settings
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import random
from django.db.models import F,Q
from django.db.models import Count
def func_class(request):
    return {'func':settings.type_choices,'fun1':settings.FUNCTION}

from django import forms
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError

class Reg(forms.Form):
    username=forms.CharField(min_length=1,required=True,
                             error_messages={'required': '用户名不能为空'},
                             widget=forms.TextInput(attrs={'class':"form-control",
                                                           'placeholder':"用户名",
                                                           }))
    password=forms.CharField(min_length=3,
                             error_messages={'required': '密码不能为空'},
                             widget=forms.TextInput(attrs={'class':"form-control",
                                                           'placeholder':"密码",
                                                           }))
    repat_password=forms.CharField(min_length=3,
                                   error_messages={'required': '密码不能为空'},
                                   widget=forms.TextInput(attrs={'class':"form-control",
                                                           'placeholder':"重新输入密码",
                                                           }))
    email=forms.EmailField(
        error_messages={'required': '邮箱不能为空'},
        widget=forms.TextInput(attrs={'class':"form-control",
                                                           'placeholder':'邮箱',
                                                           }))
    valid_code=forms.CharField(
        error_messages={'required': '验证码不能为空'},
        widget=forms.TextInput(attrs={'class':"form-control",
                                                           'placeholder':'验证码',
                                                           }))

    def __init__(self, request, *args, **kwargs):
        super(Reg,self).__init__(*args, **kwargs) #继承父类的方法
        self.request = request                    #重写父类的方法

    def clean_password(self):#局部钩子 函数名clean_字段
        if len(self.cleaned_data.get('password')) > 1:
            return self.cleaned_data.get('password')
        else:
            raise ValidationError('密码长度不能小于2位')

    def clean_username(self):
        if self.cleaned_data.get('username').isalpha():  #注意这是obj.is_valid()方法内的钩子函数，如果输入空，则self.cleaned_data没有password。
            return self.cleaned_data.get('username')  #return cleaned_data['字段']
        else:
            raise ValidationError('用户名不能包含数字！')

    def clean_valid_code(self):
        if self.cleaned_data.get('valid_code').upper()==self.request.session["valid_code"].upper():
            return self.cleaned_data.get('valid_code')
        else:
            raise ValidationError('验证码错误')



    def clean(self): #全局钩子方法 对全局 lean（）
        if self.cleaned_data.get('password') ==self.cleaned_data.get('repat_password'):
            return self.cleaned_data  #return cleaned_data
        else:
            raise ValidationError('密码不一致！')

class Commenform(forms.Form):

    content=forms.CharField( error_messages={'required': '评论不能为空'},
                            widget=forms.Textarea(attrs={'cols':'30','id':"comment_content",
                                                         'class': "content",
                                                         'rows': "10",
                                                          }))

def log_in(request):
    if request.method=='GET':
        nextpath=request.GET.get('next','/index/')
        return render(request,'login1.html',locals())

    else:
        username=request.POST.get('username')
        password=request.POST.get('password')
        #密码zhanggen123.com
        valid_code=request.POST.get('valid_code')
        #设置统一报错信息
        ajax_response = {"user": None, "errors": ""}
        #如果验证和 session中设置的验证码一致，
        if valid_code.upper()==request.session.get('valid_code').upper():
            # 进行用户验证
            user=authenticate(username=username,password=password)
            if user:
                login(request,user)
                ajax_response['user']=user.username
            else:
                ajax_response['errors'] ='用户名/密码错误'
        else:
            ajax_response['errors'] = '验证码错误'
        return HttpResponse(json.dumps(ajax_response))

def valid_code(request):
    f = BytesIO()
    img = Image.new(mode='RGB', size=(120, 30),
                    color=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
    draw = ImageDraw.Draw(img, mode='RGB')
    font = ImageFont.truetype("static/dist/fonts/kumo.ttf", 28)
    code_list = []
    for i in range(5):
        char = random.choice([chr(random.randint(65, 90)), str(random.randint(1, 9))])
        code_list.append(char)
        draw.text([i * 24, 0], char, (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)),
                  font=font)
    img.save(f, "png")
    valid_code = ''.join(code_list)
    #以上代码就是在服务端生产验证码
    #把验证码记录到session
    request.session["valid_code"] = valid_code
    return HttpResponse(f.getvalue())

def reg(request):
    if request.method=='GET':
        obj=Reg(request)
        return render(request,'register.html',locals())
    else:
        response = {"flag": False, "errors": ""}
        obj=Reg(request,request.POST)
        if obj.is_valid():
            data=obj.cleaned_data
            username=data['username']
            password=data['password']
            email=data['email']
            avatar=request.FILES.get('img')
            models.UserInfo.objects.create_user(username=username,password=password,email=email,avatar=avatar)
            response["flag"]=True
            return HttpResponse(json.dumps(response))
        else:
            errors=obj.errors
            response["errors"]=errors
            return HttpResponse(json.dumps(response))

def index(request,**kwargs):
    #用于在前端做高亮判断和 分类切换
    #分类：如果使用url pathc传参数，{'article_type_id': '1'},没有取0
    current_type_choices_id = int(kwargs.get("article_type_id",0))
    #fifter（none）
    if kwargs.get('article_type_id')=='1':
        article_list = models.Article.objects.filter(category__title__icontains='Django')
    elif  kwargs.get('article_type_id')=='2':
        article_list = models.Article.objects.filter(category__title__icontains='Linux')
    elif  kwargs.get('article_type_id')=='3':
        article_list = models.Article.objects.filter(category__title__icontains='前端')
    elif  kwargs.get('article_type_id')=='4':
        article_list = models.Article.objects.filter(category__title__icontains='Openstack')
    else:
        article_list = models.Article.objects.filter(**kwargs)
        article_list=models.Article.objects.all()
    return render(request,'index.html',locals())

def homesite(request,**kwargs):
    blog_obj = models.Blog.objects.filter(**kwargs).first()
    tags=models.Tag.objects.filter(blog=blog_obj).all()
    # ret=[]
    # for tag in tags:
    #     temp=[]
    #     temp.append(tag.title)
    #     count=models.Article.objects.filter(blog=blog_obj).filter(tags=tag).count()
    #     temp.append(count)
    #     ret.append(temp)
    # print(ret)
    # [['shell脚本', 1], ['操作系统', 1], ['函数作用域', 2], ['linx应用安装、部署', 1]]
    models.Article.objects.filter(blog=blog_obj).values('title')
    tags_ret=models.Article.objects.filter(blog=blog_obj).values('tags__title').annotate(Count('nid'))
    category_ret=models.Article.objects.filter(blog=blog_obj).values('category__title').annotate(Count('nid'))
    times=models.Article.objects.filter(blog=blog_obj).extra(
        select={'ctime':"strftime('%%Y-%%m-%%d',create_time)"}).values('ctime').annotate(ct=Count('nid'))
    article_list = models.Article.objects.filter(blog=blog_obj)
    # ret=[]
    # for i in times:
    #     date=i["create_time"]
    #     if date:
    #         t=date.strftime('%Y-%m-%d')
    #         a = models.Article.objects.filter(blog=blog_obj).filter(create_time__icontains=t).count()
    #         if t not in ret:
    #             ret.append(t)
    #             ret.append(a)
    #         # elif t in ret and a not in ret[t]  :
    #         #     ret[t].append(a)
    #
    # ret=[ret]
    if request.GET.get('nid'):
        nid=request.GET.get('nid')
        artic=models.Article.objects.filter(nid=nid).first()
        detics=artic.articledetail.content
        comment_list=models.Comment.objects.filter( article=artic)
        obj=Commenform()
        return render(request,'read_artic.html',locals())
    return render(request,'homesite.html',locals())

def poll(request):
    respose={'flag':False}
    user_id=request.user.nid
    article_id=request.POST.get('artic_id')
    if models.ArticleUpDown.objects.filter(user_id=user_id,article_id=article_id):
        respose = {'flag': True}
    else:
        models.ArticleUpDown.objects.create(user_id=user_id,article_id=article_id)
        models.Article.objects.filter(nid=article_id).update(up_count=F('up_count')+1)
    return HttpResponse(json.dumps(respose))

def comment(request):
    responses={'flag':True,'msg':None}
    obj=Commenform(request.POST)
    if obj.is_valid():
        content=obj.cleaned_data['content']
        article_id=request.POST.get('article_id')
        user_id=request.user.nid
        parent_id_id=request.POST.get('parent_id_id',)
        comment_obj=models.Comment.objects.create(article_id=article_id,
                                      content=content,
                                      parent_id_id=parent_id_id,
                                      user_id=user_id,
                                      )
        responses['create_time']=str(comment_obj.create_time)[:16]
        models.Article.objects.filter(nid=article_id).update(
                                comment_count=F('comment_count')+1)
    else:
        responses['flag']=False
        responses['msg']=obj.errors
    return HttpResponse(json.dumps(responses))

def homesite_query(request,**kwargs):
    blog_obj = models.Blog.objects.filter(site=kwargs.get("site")).first()
    models.Article.objects.filter(blog=blog_obj).values('title')
    tags_ret = models.Article.objects.filter(blog=blog_obj).values('tags__title').annotate(Count('nid'))
    category_ret = models.Article.objects.filter(blog=blog_obj).values('category__title').annotate(Count('nid'))
    times = models.Article.objects.filter(blog=blog_obj).extra(
        select={'ctime': "strftime('%%Y-%%m-%%d',create_time)"}).values('ctime').annotate(ct=Count('nid'))
    if kwargs.get('condition')=='tag':
        blog=kwargs.get('site')
        para=kwargs.get('para')
        tag=models.Tag.objects.filter(title__contains=para).first()
        article_list=models.Article.objects.filter(blog__site=blog).filter(tags=tag)
    elif  kwargs.get('condition')=='category':
        blog = kwargs.get('site')
        para = kwargs.get('para')
        category=models.Category.objects.filter(title__contains=para)
        article_list = models.Article.objects.filter(blog__site=blog).filter(category=category)
    elif kwargs.get('condition')=='date':
        blog = kwargs.get('site')
        para = kwargs.get('para')
        article_list=models.Article.objects.filter(blog__site=blog).filter(create_time__icontains=para)
    return render(request,'homesite.html',locals())

def log_out(request):
    logout(request)
    return redirect('/index/')

#----------------文章管理视图

def back_index(request):
    bolg=request.user.blog
    article_list=models.Article.objects.filter(blog__title=bolg)
    return render(request,'backIndex.html',locals())
from bs4 import BeautifulSoup
def add_article(request):
    bolg = request.user.blog
    tags = models.Tag.objects.filter(blog=bolg)
    category = models.Category.objects.filter(blog=bolg)
    article_type=models.Article.type_choices
    if request.method=='GET':
        return render(request, 'add_article.html',locals())
    content=request.POST.get('content')
    invalid_lable=['script','link']
    BS=BeautifulSoup(content,'html.parser')
    for lable in BS:
        if lable.name in invalid_lable:
            lable.decompose()
    adddict={}
    adddict['title']=request.POST.get('title')
    adddict['desc']=request.POST.get('desc')
    adddict['category_id']=request.POST.get('category')
    adddict['article_type_id']=request.POST.get('article_type')
    adddict['blog_id']=bolg.nid
    articleobj=models.Article.objects.create(** adddict)
    content=str(BS)
    tags = request.POST.get('tags').split(',')
    tag_list=[]
    for tag in tags:
        if tag.isdigit():
            tag=int(tag)
            tag_list.append(tag)
    tags_obj=models.Tag.objects.filter(nid__in=tags)
    for i in tags_obj:
        models.Article2Tag.objects.create(article=articleobj,tag=i)
    models.ArticleDetail.objects.create(content=content,article_id=articleobj.nid)
    return HttpResponse('OK')


def upload_file(request):
    file_obj=request.FILES.get('imgFile')
    with open('/Blog_system/media/upload/image/'+file_obj.name,'wb') as f:
        for chunk in file_obj.chunks():
            f.write(chunk)
    resposes={'error':0,'url':'/media/upload/image/'+file_obj.name}
    return HttpResponse(json.dumps(resposes))




def delet_article(request):
    nid=request.GET.get('nid')
    models.Article.objects.filter(nid=nid).delete()
    models.ArticleDetail.objects.filter(article_id=nid).delete()
    models.Article2Tag.objects.filter(article_id=nid).delete()
    return redirect('/back_index/')











# msg_list = [
#     {'id':1,'content':'刘庚评论说 我来自山西大同','parent_id':None},
#     {'id':2,'content':'吴永强 评论说 来自山西临汾','parent_id':None},
#     {'id':3,'content':'由秦兵 评论说 我来自湖南娄底','parent_id':None},
#     {'id':4,'content':'高路川对刘庚说 大同市古城啊！','parent_id':1},
#     {'id':5,'content':'方少伟对高路川说 呵呵 现代人造的古城','parent_id':4},
#     {'id':6,'content':'陈涛对吴永强说 临汾出汾酒','parent_id':2},
#     {'id':7,'content':'阮国栋对少少伟说 现代人也能造古城？','parent_id':5},
#     {'id':8,'content':'武配齐对游勤斌说 娄底咋 出了这败类？','parent_id':3},
# ]

def comment_tree(request):
    article_nid = request.GET.get('nid')
    artic = models.Article.objects.filter(nid=article_nid).first()
    detics = models.ArticleDetail.objects.filter(article_id=article_nid).first()
    if request.is_ajax():
        comments_list=models.Comment.objects.filter(article_id=article_nid).values('nid','content','parent_id_id')
        comments_dict = {}
        for row in comments_list:                    #把评论从数据库获取处理
            row['child']=[]                          #添加 child建 盛放子评论
            nid=row['nid']                           #定于个字典
            comments_dict[nid]=row

        for key in comments_dict:                        #遍历所有评论
            if comments_dict[key]['parent_id_id']:     #获取到有父评论的子评论
                pid= comments_dict[key]['parent_id_id'] #找到子评论的在字典中父评论ID
                comments_dict[pid]['child'].append(comments_dict[key])  #把子评论添加到对应父评论


        ret=[]
        for key in  comments_dict:       #从字典中获取根评论
            if not comments_dict[key]['parent_id_id']:
                ret.append(comments_dict[key])
        return HttpResponse(json.dumps(ret))
    return render(request,'comment_tree.html',locals())


from django.views import View
class CBV(View):
    def get(self,request,**kwargs):
        return render(request,'test.html')
    def post(self,request,**kwargs):
        return HttpResponse('ok')











