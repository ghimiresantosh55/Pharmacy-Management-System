from django.db import models
# from src.pims_app.models import NowTimestampAndUserModel
# from src.pims_app.models import Province, District
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken

from django.contrib.auth.models import AbstractBaseUser, \
    PermissionsMixin, BaseUserManager
from django.conf import settings
# email settings
from django.core.mail import EmailMultiAlternatives
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.urls import reverse
from django_rest_resetpassword.signals import reset_password_token_created
from pims import settings
from django.core.exceptions import ValidationError
from src.user_group.models import CustomGroup
from tenant.utils import hostname_from_request
# imports for log
from simple_history import register
from log_app.models import LogBase
from src.custom_lib.functions.date_converter import ad_to_bs_converter


@receiver(reset_password_token_created)
def reset_password_token_created(sender, instance, reset_password_token, *args, **kwargs):
    """
    Handles password reset tokens
    When a token is created, an e-mail needs to be sent to the user
    :param sender: View Class that sent the signal
    :param instance: View Instance that sent the signal
    :param reset_password_token: Token Model Object
    :param args:
    :param kwargs:
    :return:
    """
    # send an e-mail to the user
    context = {
        'current_user': reset_password_token.user,
        'user_name': reset_password_token.user.user_name,
        'email': reset_password_token.user.email,
        # 'domain': "pims-backend.staging.merakitechs.com",
        'domain': "http://localhost:3000",
        # 'reset_password_url': "{}?token={}".format(reverse('password_reset:reset-password-request'), reset_password_token.key)
        'reset_password_url': "{}{}".format("/reset-password/confirm/", reset_password_token.key)

    }

    # render email text
    email_html_message = render_to_string('email.html', context)
    # email_plaintext_message = render_to_string('email/user_reset_password.txt', context)
    email_plaintext_message = "{}?token={}".format(reverse('password_reset:reset-password-request'),
                                                   reset_password_token.key)
    msg = EmailMultiAlternatives(
        # title:
        "Password Reset for {title}".format(title="Some website title"),
        # message:
        email_plaintext_message,
        # from:
        "noreply@somehost.local",
        # to:
        [reset_password_token.user.email]
    )
    msg.attach_alternative(email_html_message, "text/html")
    msg.send()


class CustomAccountManager(BaseUserManager):

    def create_superuser(self, email, user_name, password, **other_fields):

        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)
        other_fields.setdefault('is_active', True)

        if other_fields.get('is_staff') is not True:
            raise ValueError(
                'Superuser must be assigned to is_staff=True.')
        if other_fields.get('is_superuser') is not True:
            raise ValueError(
                'Superuser must be assigned to is_superuser=True.')

        return self.create_user(email, user_name, password, **other_fields)

    def create_user(self, email, user_name, password, **other_fields):

        if not email:
            raise ValueError('You must provide an email address')

        email = self.normalize_email(email)
        user_name = user_name.lower()
        user = self.model(email=email, user_name=user_name, **other_fields)
        user.set_password(password)
        user.save()
        return user


def upload_path_user(instance, filename):
    return '/'.join(['user_image', filename])


def validate_image(image):
    file_size = image.size
    limit_byte_size = settings.MAX_UPLOAD_SIZE
    if file_size > limit_byte_size:
        # converting into kb
        f = limit_byte_size / 1024
        # converting into MB
        f = f / 1024
        raise ValidationError("Max size of file is %s MB" % f)


class User(AbstractBaseUser, PermissionsMixin):
    GENDER_TYPE = (
        (1, "Male"),
        (2, "Female"),
        (3, "Other")
    )
    email = models.EmailField(max_length=150, help_text='email address max length: 150 characters', unique=True)
    user_name = models.CharField(max_length=50, unique=True,
                                 help_text="user_name must be unique and max_length upto 50 characters")
    first_name = models.CharField(max_length=50, blank=True,
                                  help_text="First name can have max_length upto 50 characters, blank=True")
    middle_name = models.CharField(max_length=50, blank=True,
                                   help_text="Middle name can have max_length upto 50 characters, blank=True")
    last_name = models.CharField(max_length=50, blank=True,
                                 help_text="Last name can have max_length upto 50 characters, blank=True")
    created_date_ad = models.DateTimeField(null=True, blank=True)
    created_date_bs = models.CharField(max_length=10, null=True, blank=True)
    is_staff = models.BooleanField(default=True,
                                   help_text="By default=True")
    is_active = models.BooleanField(default=False)
    gender = models.PositiveIntegerField(choices=GENDER_TYPE, default=1,
                                         help_text="where 1=male, 2=Female and 3=Other, default=1")
    birth_date = models.DateField(null=True, blank=True, help_text="Blank=True and null=True")
    address = models.TextField(max_length=50, blank=True, help_text="Address should be maximum of 50 characters")
    mobile_no = models.CharField(max_length=15, blank=True, help_text="Mobile no. should be maximum of 15 characters")
    photo = models.ImageField(upload_to=upload_path_user, validators=[validate_image], blank=True)
    group = models.ForeignKey(CustomGroup, on_delete=models.PROTECT, blank=True, null=True, related_name='user_group')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True)
    objects = CustomAccountManager()

    REQUIRED_FIELDS = ['email']
    USERNAME_FIELD = 'user_name'

    # @property
    # def group_name(self):
    #     user=User.objects.get(pk=id)
    #     group_name = user.group_name
    #     return "user_%s" % self.id

    def __str__(self):
        return "id {} : {}".format(self.pk, self.user_name)

    def tokens(self, request):
        refresh = RefreshToken.for_user(self)
        host_name = hostname_from_request(request)
        refresh['domain_name'] = host_name
        refresh['user_name'] = self.user_name
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }

    def save(self, *args, **kwargs):
        if not self.pk:
            self.created_date_ad = timezone.now()
            date_bs = ad_to_bs_converter(self.created_date_ad)
            self.created_date_bs = date_bs

        super().save(*args, **kwargs)


register(User, app="log_app", table_name="user_user_log",
         custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])
