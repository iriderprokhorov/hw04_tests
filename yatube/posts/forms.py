from django import forms

from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = (
            "text",
            "group",
        )
        help_texts = {
            "text": "something about text",
            "group": "something about group",
        }

    def clean_text(self):
        data = self.cleaned_data["text"]
        if not data:
            raise forms.ValidationError("Please fill empty field")
        return data
