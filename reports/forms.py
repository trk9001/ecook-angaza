from django import forms


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())


class ImportForm(forms.Form):
    csv = forms.FileField(label='Upload a CSV')
