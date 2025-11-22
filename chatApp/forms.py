from django import forms
from .models import BlogPost


class BlogPostForm(forms.ModelForm):
    tags_input = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'placeholder': 'Etiquetas separadas por comas (p.ej. Santiago,almacen)'}))

    class Meta:
        model = BlogPost
        fields = ['title', 'content', 'image', 'published']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Título'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 8, 'placeholder': 'Contenido de la entrada...'}),
        }

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if not image:
            return image

        # tamaño máximo 5MB
        max_size = 5 * 1024 * 1024
        if image.size > max_size:
            raise forms.ValidationError(
                'La imagen es demasiado grande (máx 5MB).')

        # tipos permitidos
        valid_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
        if hasattr(image, 'content_type') and image.content_type not in valid_types:
            raise forms.ValidationError(
                'Formato de imagen no válido. Use JPG, PNG, GIF o WEBP.')

        return image

    def save(self, commit=True, author=None):
        # Override save to handle tags_input
        post = super().save(commit=False)
        if author:
            post.author = author
        if commit:
            post.save()
            # process tags
            tags_text = self.cleaned_data.get('tags_input', '')
            if tags_text is not None:
                tag_names = [t.strip()
                             for t in tags_text.split(',') if t.strip()]
                from .models import Tag
                post.tags.clear()
                for name in tag_names:
                    tag_obj, _ = Tag.objects.get_or_create(name=name)
                    post.tags.add(tag_obj)
        return post
