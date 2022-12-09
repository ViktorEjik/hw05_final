from django import forms
from django.contrib.auth import get_user_model

from .models import Comment, Post

User = get_user_model()


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')

    def clean_text(self):
        value = self.cleaned_data['text']
        if value == '':
            raise forms.ValidationError('Поле text не должно быть пустым!')
        return value


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)

    def clean_text(self):
        value = self.cleaned_data['text']
        if value == '':
            raise forms.ValidationError('Поле text не должно быть пустым!')
        return value
