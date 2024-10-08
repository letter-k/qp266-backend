import graphene
from django.contrib.auth import authenticate, get_user_model
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from rest_framework.authtoken.models import Token

User = get_user_model()


class AuthArguments(graphene.InputObjectType):
    username = graphene.String(required=True)
    password = graphene.String(required=True)


class ObtainAuthToken(graphene.Mutation):
    class Arguments:
        credentials = AuthArguments()

    token = graphene.String()

    def mutate(self, info, credentials: AuthArguments):
        user = authenticate(username=credentials.username, password=credentials.password)
        if user is None:
            raise Exception("Invalid username or password")

        token, created = Token.objects.get_or_create(user=user)
        return ObtainAuthToken(token=token.key)


class RegisterArguments(graphene.InputObjectType):
    username = graphene.String(required=True)
    email = graphene.String(required=True)
    password = graphene.String(required=True)


class UserRegister(graphene.Mutation):
    class Arguments:
        credentials = RegisterArguments()

    msg = graphene.String()

    def mutate(self, info, credentials: RegisterArguments):
        user = User.objects.filter(email=credentials.email).first()

        if user:
            email_subject = "Registration Attempt Detected"
            email_body = render_to_string(
                "email/registration_attempt_email.html",
                {
                    "username": credentials.username,
                    "email": credentials.email,
                },
            )

            email = EmailMessage(
                subject=email_subject,
                body=email_body,
                from_email="no-reply@qp266.ru",
                to=[user.email],
            )
            email.content_subtype = "html"
            email.send()

            return UserRegister(msg="User created and email sent!")

        user = User.objects.create_user(
            username=credentials.username,
            email=credentials.email,
            password=credentials.password,
        )

        email_subject = "Welcome to qp266!"
        email_body = render_to_string("email/welcome_email.html", {"username": user.username})

        email = EmailMessage(
            subject=email_subject,
            body=email_body,
            from_email="no-reply@qp266.ru",
            to=[user.email],
        )
        email.content_subtype = "html"
        email.send()

        return UserRegister(msg="User created and email sent!")
