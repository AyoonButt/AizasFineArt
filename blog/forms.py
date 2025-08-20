from django import forms
from .models import BlogComment, BlogSubscriber


class BlogCommentForm(forms.ModelForm):
    class Meta:
        model = BlogComment
        fields = ['author_name', 'author_email', 'author_website', 'content']
        widgets = {
            'author_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Your name',
                'required': True
            }),
            'author_email': forms.EmailInput(attrs={
                'class': 'form-input',
                'placeholder': 'your.email@example.com',
                'required': True
            }),
            'author_website': forms.URLInput(attrs={
                'class': 'form-input',
                'placeholder': 'https://yourwebsite.com (optional)'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-textarea',
                'placeholder': 'Share your thoughts...',
                'rows': 4,
                'required': True
            }),
        }
        
    def clean_content(self):
        content = self.cleaned_data['content']
        if len(content.strip()) < 10:
            raise forms.ValidationError('Comment must be at least 10 characters long.')
        return content


class NewsletterSubscribeForm(forms.ModelForm):
    class Meta:
        model = BlogSubscriber
        fields = ['email', 'name']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter your email address',
                'required': True
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Your name (optional)'
            }),
        }
        
    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        return email