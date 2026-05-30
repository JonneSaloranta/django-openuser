import random

from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin)
from django.core.validators import MinLengthValidator, RegexValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField


class CustomAccountManager(BaseUserManager):

    def create_superuser(
        self, email, username, firstname, lastname, password, **other_fields
    ):
        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)
        other_fields.setdefault('is_active', True)

        if other_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must be assigned to is_staff=True.'))
        if other_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must be assigned to is_superuser=True.'))

        return self.create_user(
            email=email,
            username=username,
            firstname=firstname,
            lastname=lastname,
            password=password,
            **other_fields,
        )

    def create_user(
        self, email, username, firstname, lastname, password, **other_fields
    ):
        if not email:
            raise ValueError(_('You must provide an email address'))

        email = self.normalize_email(email)
        user = self.model(
            email=email,
            username=username,
            firstname=firstname,
            lastname=lastname,
            **other_fields,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user


def user_avatar_upload_path(instance, filename):
    return f'user_{instance.id}/{timezone.now():%Y/%m/%d}/{filename}'


class CustomUser(AbstractBaseUser, PermissionsMixin):

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')

    alphanumeric_validator = RegexValidator(
        r'^[0-9a-zA-Z]*$',
        _('Enter a valid username. Letters and digits only.'),
        'invalid',
    )

    email = models.EmailField(_('email address'), unique=True)
    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        help_text=_(
            'Username must be between 4 and 150 characters. Letters and digits only.'
        ),
        validators=[MinLengthValidator(4), alphanumeric_validator],
        error_messages={
            'unique': _('An user with that username already exists.'),
        },
    )
    profile_picture = models.ImageField(
        blank=True, upload_to=user_avatar_upload_path
    )
    firstname = models.CharField(_('firstname'), max_length=150)
    lastname = models.CharField(_('lastname'), max_length=150)
    phonenumber = PhoneNumberField(
        _('phone number'),
        region='FI',
        blank=True,
        help_text=_('Contact phone number'),
    )
    address = models.CharField(_('address'), max_length=50, blank=True)
    postal_code = models.CharField(
        _('postal code'), max_length=5, blank=True
    )
    city = models.CharField(_('city'), max_length=50)

    info = models.TextField(_('info'), max_length=500, blank=True)

    join_date = models.DateTimeField(_('join date'), auto_now_add=True)
    last_online = models.DateTimeField(_('last online'), blank=True, auto_now_add=True)
    member_id = models.CharField(_('member id'), unique=True, blank=True)

    is_staff = models.BooleanField(_('is staff'), default=False)
    is_active = models.BooleanField(_('is active'), default=False)
    is_private = models.BooleanField(_('is private'), default=True)

    objects = CustomAccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'firstname', 'lastname']

    def __str__(self):
        return self.username

    @property
    def is_online(self):
        '''Returns True if user active within last 5 minutes.'''
        if not self.last_online:
            return False
        return timezone.now() - self.last_online <= timezone.timedelta(minutes=5)

    def get_absolute_url(self):
        return reverse(
            'django_openuser:profile_details', kwargs={'username': self.username}
        )

    def generate_member_id(self):
        '''Generate a unique member_id based on initials + year suffix + 3 random digits.'''
        initials = (self.firstname[0] + self.lastname[0]).upper()
        join_date = self.join_date or timezone.now()
        year_suffix = str(join_date.year)[-2:]

        for _ in range(100):
            random_digits = f'{random.randint(0, 999):03d}'
            member_id = f'{initials}{year_suffix}{random_digits}'
            if not CustomUser.objects.filter(member_id=member_id).exists():
                return member_id

        raise ValueError('Failed to generate unique member ID after 100 attempts.')

    def save(self, *args, **kwargs):

        if not self.member_id and self.firstname and self.lastname:
            self.member_id = self.generate_member_id()

        super().save(*args, **kwargs)
