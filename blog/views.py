from django.shortcuts import render, redirect  # Function Based View 를 사용했습니다
from .models import Post, Category, Tag, Comment
from django.views.generic import ListView # 게시판형으로 데이터를 가지고 오는 클래스 
from django.views.generic.detail import DetailView
from django.views.generic import CreateView, UpdateView
from django.core.exceptions import PermissionDenied # 인가 - 권한이 있는 사용자만
from django.utils.text import slugify # 빈칸이나 특수문자로 이루어진 문장을 대시 등을 이용한 한 단어로 이어묶어주는 모듈
from django.db.models import Q
from django.shortcuts import get_object_or_404
from .forms import CommentForm
from django.contrib.auth import authenticate, login


# Login 기능 위해 Mixin 추가 
# Mixin은 객체 지향 프로그램에서 많이 쓰이는 개념으로 간단하게 말하여 다중상속을 가능하게 하는 클래스라고 할 수 있다. 여타의 언어들과는 다르게 파이썬은 다중 상속이 지원되지만 다중상속이 주는 모호함을 피하기 위해 많이 사용한다. 
# 따라서 Mixin은 상속이라기 보다는 포함, 확장이라는 개념으로 생각할 수 있다.
# 장고의 Mixin-메인 기능(비즈니스 로직)에 
# 인증, 로그 등 여러 부가 기능 사용 위해 다중상속 가능케하는 클래스
# 클래스에 Mixin 사용시 다른 클래스의 메서드 추가 가능
from django.contrib.auth.mixins import LoginRequiredMixin

# 화면 들어가서 확인 
# Mixin을 앞에 넣어줘야 인증 먼저 하고 해당 페이지로 넘어감
# LoginRequiredMixin은 사용자의 페이지에 로그인 되지 않은 다른 사용자가 접근하지 못하게 하고 로그인 페이지로 이동하게 하는 기능을 가지고 있는 클래스이다.
# 완성 후 실습: 글쓰기 버튼도 로그인한 사용자만 보이도록 변경해보세요 
class PostCreate(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['title', 'content', 'header_img', 'file_upload', 'category']
    # tag -> #카지노 #카지노_행님_20만원만 unique=True : 여러개 달았을 때 이미 있는 해시태그는 더 등록되지 않도록 
    # author -> 로그인 하는 순간부터 author 는 남아있기 때문에
    # created_at -> 작성되는 순간 자동 등록  
    # updated_at -> 수정되는 순간 자동 등록

    # CreateView가 내장 - 오버라이딩
    # 방문자가 form에 담에 보낸 유효한 정보를 담아 포스트를 만들고,
    # 이 포스트의 고유경로로 재전송(redirect)해주는 역할 
    # def form_valid(self, form):
    #     current_user = self.request.user
    #     if current_user.is_authenticated:
    #         form.instance.author = current_user
    #         return super(PostCreate, self).form_valid(form)
    #     else:
    #         return redirect('/blog/')

    # Tag 입력기능 추가
    # 포스트에 태그를 추가하려면 이미 데이터베이스에 저장된 pk를 부여받아서 수정해야 함, 그래서 form_valid()를 통해 결과를 response 변수에 임시 담아두고
    # 서로 저장된 포스트를 self.object로 저장함.
    def form_valid(self, form):
        current_user = self.request.user
        if current_user.is_authenticated and (current_user.is_staff or current_user.is_superuser):
            form.instance.author = current_user
            response = super(PostCreate, self).form_valid(form)

            tags_str = self.request.POST.get('tags_str')
            if tags_str:
                tags_str = tags_str.strip()

                tags_str = tags_str.replace(',', ';')
                tags_list = tags_str.split(';')

                for t in tags_list:
                    t = t.strip()
                    tag, is_tag_created = Tag.objects.get_or_create(tagName=t)
                    if is_tag_created:
                        tag.slug = slugify(t, allow_unicode=True)
                        tag.save()
                    self.object.tag.add(tag)

            return response

        else:
                return redirect('/blog/')

# urls -> views -> templates(post_detail.html에 Edit 버튼 추가)
class PostUpdate(LoginRequiredMixin, UpdateView):
    model = Post
    # fields = ['title', 'content', 'header_img', 'file_upload', 'category', 'tag']
    fields = ['title', 'content', 'header_img', 'file_upload', 'category']
    
    # 로그인한 상태에서 작성자(request.user) 가 object.author(Post.objects.get(pk=pk))과 일치하는지 확인 필요
    def dispatch(self, request, *args, **kwargs): # 방문자가 GET으로 요청했는데 POST로 요청했는지 확인하는 기능
        if request.user.is_authenticated and request.user == self.get_object().author:
            return super(PostUpdate, self).dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied # 권한 없는 사람이 글 수정하려 하면 403

    # author 필드는 당연히 이전에 글을 생성한 작성자로 채워져있고, LoginRequiredMixin으로 로그인한 유저 확인하므로 form_valid는 오버라이딩하지 않음
    # 태그에 여러개 보내면 겹치지 않는 것만 새로 성성하는 기능은 필요하므로 get_context_data를 오버라이딩
    def get_context_data(self, **kwargs):
        context = super(PostUpdate, self).get_context_data()
        if self.object.tag.exists():
            tags_str_list = list()
            for t in self.object.tag.all():
                tags_str_list.append(t.tagName)
            context['tags_str_default'] = '; '.join(tags_str_list)

        return context

    # 포스트에 태그를 추가하려면 이미 데이터베이스에 저장된 pk를 부여받아서 수정해야 함, 그래서 form_valid()를 통해 결과를 response 변수에 임시 담아두고
    # 서로 저장된 포스트를 self.object로 저장함.
    def form_valid(self, form):
        response = super(PostUpdate, self).form_valid(form)
        self.object.tag.clear()

        tags_str = self.request.POST.get('tags_str')
        if tags_str:
            tags_str = tags_str.strip()
            tags_str = tags_str.replace(',', ';')
            tags_list = tags_str.split(';')

            for t in tags_list:
                t = t.strip()
                tag, is_tag_created = Tag.objects.get_or_create(tagName=t)
                if is_tag_created:
                    tag.slug = slugify(t, allow_unicode=True)
                    tag.save()
                self.object.tag.add(tag)

        return response

class BlogHome(ListView):
    model = Post
    ordering = '-pk' 
    template_name = 'blog/blog_home.html'
    context_object_name = 'posts'

    # ListView를 상속받으면서 전달받은 get_context_data라는 함수를 오버라이딩합니다
    def get_context_data(self, **kwargs): # 함수의 파라미터를 개수 안 정해서 k-v 순으로 만들어 보내겠다
        # 속성명 = 값 -> 파이썬의 namespace에서는 키:밸류 순으로 관리됩니다
        context = super(BlogHome, self).get_context_data(**kwargs)
        context['first_post'] = Post.objects.all().last() # first_post라는 이름으로 하나 더 값을 만들어서 전달할게요
        # 필요한 값들을 ORM으로 뽑아서 가져올 수 있습니다.
        return context


class PostList(ListView):  # post_list 라고 생긴 template과 model을 조합합니다. 
    model = Post
    ordering = '-pk' 
    paginate_by = 5 # n개씩 잘라서 data(record)를 전송해주는 속성. views.py에서도, urls.py도 줄 수 있습니다
    paginate_orphans = 3 # 자투리 101개 있음 -> 5개씩 값을 꺼내오면 마지막 남는 1개(orphan)가 있음...
                        # 디자인 깨지지 않게 5개씩 꺼내올 때 값이 2개 이하이면 마지막 페이지에 걍 붙여버려

    # post_list에 전달할 전체 객체명을 바꿔줍니다.
    context_object_name = 'posts'

    # ListView를 상속받으면서 전달받은 get_context_data라는 함수를 오버라이딩합니다
    def get_context_data(self, **kwargs): # 함수의 파라미터를 개수 안 정해서 k-v 순으로 만들어 보내겠다
        # 속성명 = 값 -> 파이썬의 namespace에서는 키:밸류 순으로 관리됩니다
        context = super(PostList, self).get_context_data(**kwargs)
        context['first_post'] = Post.objects.all().last() # first_post라는 이름으로 하나 더 값을 만들어서 전달할게요
        context['categories'] = Category.objects.all()
        # 그냥 post_list.html에서 미분류의 개수를 세서 숫자를 표기해주기 위한 ORM 쿼리
        context['no_category_post_count'] = Post.objects.filter(category=None).count() 
        # 필요한 값들을 ORM으로 뽑아서 가져올 수 있습니다.
        return context

    
# blog 폴더(앱)에서 post_detail.html로 가고 있는 객체를 posts라고 이름을 변경해보세요
# 해당 변수명으로 받은 객체들에 더해 subject 라는 이름으로 제목 데이터만 전달하는 추가 변수를 달아주세요

class PostDetail(DetailView):  # post_detail 라고 생긴 template과 model을 조합합니다. 
    model = Post
    # context_object_name = 'posts'

    def get_context_data(self, **kwargs): # 함수의 파라미터를 개수 안 정해서 k-v 순으로 만들어 보내겠다
        # 속성명 = 값 -> 파이썬의 namespace에서는 키:밸류 순으로 관리됩니다
        context = super(PostDetail, self).get_context_data(**kwargs)
        # print(context['object']) # 뭐가 들어있나 확인해보세요
        context['subject'] = context['object'].title 
        # 필요한 값들을 ORM으로 뽑아서 가져올 수 있습니다.
        context['comment_form'] = CommentForm
        return context

def category_posts(request, slug):
    if slug == "no_category":
        posts = Post.objects.filter(category=None)
    else:
        category = Category.objects.get(slug=slug)
        posts = Post.objects.filter(category=category)

    # 카테고리가 없으면 None을 가지고 있는 값을 보냅니다.
    return render(
        request,
        'blog/post_list.html',
        {
            'posts' : posts,
            'categories' : Category.objects.all(),
            'no_category_post_count' : Post.objects.filter(category=None).count()
            # 카테고리 위젯을 잘 완성시키기 위해 만들어야 되는 변수들
            # no_category 글의 개수 세기기 count()
            # Post.objects.filter(category=None)를 호출하도록 urls도 변경해야 할겁니다

        }

    )

def tag_posts(request, slug):
    if slug == "no_tag":
        posts = Post.objects.filter(tag=None)
    else:
        tag = Tag.objects.get(slug=slug)
        posts = Post.objects.filter(tag=tag)

    # 카테고리가 없으면 None을 가지고 있는 값을 보냅니다.
    return render(
        request,
        'blog/post_list.html',
        {
            'posts' : posts,
            'tag' : tag,
            'categories' : Category.objects.all(),
            'no_category_post_count' : Post.objects.filter(category=None).count()
        }

    )



def about_me(request):
    return render(
        request,
        'blog/about.html'
    )

def contact(request):
    return render(
        request,
        'blog/contact.html'
    )

# 코멘트 기능
def new_comment(request, pk):
    if request.user.is_authenticated:
        post = get_object_or_404(Post, pk=pk)

        if request.method == 'POST':
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.post = post
                comment.author = request.user
                comment.save()
                return redirect(comment.get_absolute_url())
        else:
            return redirect(post.get_absolute_url())
    else:
        raise PermissionDenied


class CommentUpdate(LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user == self.get_object().author:
            return super(CommentUpdate, self).dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied


def delete_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk) # 댓글을 달 포스트를 가져오거나 404 에러를 발생합니다.
    post = comment.post
    if request.user.is_authenticated and request.user == comment.author:
        comment.delete()
        return redirect(post.get_absolute_url())
    else:
        raise PermissionDenied

# 검색창으로 들어온 포스트
class PostSearch(PostList):
    paginate_by = None

    def get_queryset(self):
        q = self.kwargs['q']
        post_list = Post.objects.filter(
            Q(title__contains=q) | Q(tag__tagName__contains=q) | Q(category__categoryName__contains=q)
        ).distinct()
        return post_list

    def get_context_data(self, **kwargs):
        context = super(PostSearch, self).get_context_data()
        q = self.kwargs['q']
        context['search_info'] = f'Search: {q} ({self.get_queryset().count()})'

        return context

# Create your views here.
# V (view) - 화면에 출력되는 부분을 책임집니다. 
# def index(request):
#     return render(
#         request, 
#         'blog/index.html'
#     )

# def index2(request):
#     return render(
#         request, 
#         'index2.html'
#     )
