import unicodedata

from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.contrib.auth.models import Group, Permission
from django.utils.crypto import get_random_string

User = get_user_model()


class UsernameField(forms.CharField):
    def to_python(self, value):
        value = super().to_python(value)
        return None if value is None else unicodedata.normalize("NFKC", value)


class UserAdminForm(UserChangeForm):
    username = UsernameField(label="Имя пользователя", required=False)
    password = forms.CharField(widget=forms.HiddenInput())
    is_staff = forms.CharField(widget=forms.HiddenInput())
    is_superuser = forms.CharField(widget=forms.HiddenInput())
    user_permissions = forms.ModelMultipleChoiceField(
        Permission.objects.all(),
        widget=FilteredSelectMultiple("права", False),
        label="Права",
        required=False,
    )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if not user.username:
            user.username = user.email
        user.save()
        return user


class UserAdminCreationForm(UserCreationForm):
    email = forms.EmailField(
        label="Email",
        help_text=(
            "Обязательное поле. На данную почту пользователю будет выслана ссылка для смены и восстановления пароля."
        ),
        required=True,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password1"].required = False
        self.fields["password2"].required = False

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if not user.username:
            user.username = user.email
        password = get_random_string(length=8)
        user.set_password(password)
        user.save()
        user.email_user("Регистрация на quick point 266: ваш пароль", f"Логин: {user.email} \nПароль: {password}")
        return user

    class Meta:
        model = User
        fields = (
            "username",
            "email",
        )
        error_messages = {
            "email": {
                "unique": "Электронная почта должна быть уникальной!",
            },
        }


class GroupAdminForm(forms.ModelForm):
    """Extra field "Users" for groups."""

    class Meta:
        model = Group
        exclude = ()

    users = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        required=False,
        widget=FilteredSelectMultiple("пользователи", False),
        label="Пользователи",
    )
    permissions = forms.ModelMultipleChoiceField(
        Permission.objects.all(),
        widget=FilteredSelectMultiple("права", False),
        label="Права",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields["users"].initial = self.instance.user_set.all()

    def save_m2m(self):
        """Add the users to the Group and remove past relations."""
        self.instance.user_set.through.objects.filter(user__in=self.cleaned_data["users"]).delete()

        self.instance.user_set.set(self.cleaned_data["users"])

    def save(self, *args, **kwargs):
        instance = super().save()
        self.save_m2m()
        return instance
