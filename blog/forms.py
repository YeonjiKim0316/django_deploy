from .models import Comment
from django import forms
from django.contrib.auth.forms import UserChangeForm
# from django.contrib.auth.models import User # 이렇게 직접적으로 참고할수는 있으나 권장하지 않는 방법임
from django.contrib.auth import get_user_model


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('content',)



class CustomUserChangeForm(UserChangeForm) :
    
    class Meta :
        # model = User
        model = get_user_model()
        fields = ('email', 'password')