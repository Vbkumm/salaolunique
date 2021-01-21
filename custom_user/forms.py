from django import forms
from .models import CustomUser
from photo.models import ServicePhotoModel


class UpdateUserForm(forms.ModelForm):
    about = forms.CharField(label='', required=False, widget=forms.Textarea(
        attrs={'rows': 4, 'placeholder': 'Uma curta descrição sobre você em até 1000 caracteres.'}
    ),
                                          max_length=1000,
                                          help_text='O maximo de caracteres permitido são 1000.',
                                          )

    class Meta:
        model = CustomUser

        fields = ('first_name', 'last_name', 'picture', 'about')


class UpdateListUserForm(forms.ModelForm):

    class Meta:
        model = CustomUser

        fields = ('is_professional',)


class PhotoBookmarkForm(forms.Form):
    photo_bookmark = forms.ModelChoiceField(queryset=ServicePhotoModel.objects.all())
