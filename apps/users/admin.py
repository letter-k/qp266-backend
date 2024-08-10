from django.contrib import admin
from django.contrib.admin.utils import quote
from django.contrib.admin.views.main import ChangeList
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import GroupAdmin as DjangoGroupAdmin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.models import Group, Permission
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from rest_framework.authtoken.models import Token, TokenProxy

from apps.users.forms import GroupAdminForm, UserAdminCreationForm, UserAdminForm
from apps.users.models import ProxyGroup, ProxyToken

User = get_user_model()


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    form = UserAdminForm
    list_display = ("username", "email", "is_active", "role", "last_login")
    list_filter = (
        "groups",
        "is_active",
    )
    fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "email",
                ),
            },
        ),
        (
            "Инфо",
            {
                "fields": (
                    "role",
                    "is_active",
                ),
            },
        ),
        (
            "Даты",
            {
                "fields": (
                    "last_login",
                    "date_joined",
                ),
            },
        ),
    )
    add_form = UserAdminCreationForm
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "email",
                ),
            },
        ),
    )
    search_fields = (
        "email",
        "username",
    )
    readonly_fields = (
        "date_joined",
        "last_login",
        "role",
    )

    @admin.display(description="Роль")
    def role(self, obj):
        return obj.groups.all()[:1]

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("groups")


admin.site.unregister(Group)


class GroupAdmin(admin.ModelAdmin):
    form = GroupAdminForm
    list_display = ["name"]
    filter_horizontal = ("permissions",)


admin.site.register(ProxyGroup, GroupAdmin)


class TokenChangeList(ChangeList):
    """Map to matching User id"""

    def url_for_result(self, result):
        pk = result.user.pk
        return reverse(
            "admin:%s_%s_change" % (self.opts.app_label, self.opts.model_name),
            args=(quote(pk),),
            current_app=self.model_admin.admin_site.name,
        )


admin.site.unregister(TokenProxy)


class TokenAdmin(admin.ModelAdmin):
    list_display = ("key", "user", "created")
    fields = ("user",)
    search_fields = ("user__username",)
    search_help_text = _("Username")
    ordering = ("-created",)
    actions = None  # Actions not compatible with mapped IDs.

    def get_changelist(self, request, **kwargs):
        print("Q")
        return TokenChangeList

    def get_object(self, request, object_id, from_field=None):
        """
        Map from User ID to matching Token.
        """
        queryset = self.get_queryset(request)
        field = User._meta.pk
        try:
            object_id = field.to_python(object_id)
            user = User.objects.get(**{field.name: object_id})
            return queryset.get(user=user)
        except (queryset.model.DoesNotExist, User.DoesNotExist, ValidationError, ValueError):
            return None

    def delete_model(self, request, obj):
        # Map back to actual Token, since delete() uses pk.
        token = Token.objects.get(key=obj.key)
        return super().delete_model(request, token)


admin.site.register(ProxyToken, TokenAdmin)
