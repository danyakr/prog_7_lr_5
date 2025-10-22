from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.utils import user_email
from django.contrib.auth import get_user_model


class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Адаптер, который мягко связывает Google-аккаунт
    с уже существующим пользователем по совпадающему email.
    """

    def pre_social_login(self, request, sociallogin):
        """
        Этот метод вызывается перед входом через Google.
        Если в базе уже есть пользователь с тем же email,
        социальный аккаунт будет привязан к нему.
        """
        # Если аккаунт уже привязан — ничего не делаем
        if sociallogin.is_existing:
            return

        user_model = get_user_model()
        email = user_email(sociallogin.user)

        if not email:
            return  # без email ничего не связываем

        try:
            # Проверяем, есть ли пользователь с таким email
            existing_user = user_model.objects.get(email__iexact=email)
            # ✅ Привязываем Google-профиль к существующему пользователю
            sociallogin.connect(request, existing_user)
        except user_model.DoesNotExist:
            pass  # если нет — будет создан новый пользователь
