# -*- coding: utf-8 -*-

"""Models for the user interface application."""

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class CustomUserManager(BaseUserManager):
    def create_user(self, email, first_name=None, last_name=None, contact_number=None, password=None):
        """Create and save a User with the given email, date of birth, and password."""
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            contact_number=contact_number
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, first_name=None, last_name=None, contact_number=None):
        """Create and save a superuser with the given email, date of birth, and password."""
        user = self.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            contact_number=contact_number,
        )
        user.is_admin = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
        db_index=True,
    )
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'

    # Profile Detail Fields
    first_name = models.CharField(max_length=128, verbose_name="First Name", null=True)
    last_name = models.CharField(max_length=128, verbose_name="Last Name", null=True)
    contact_number = models.BigIntegerField(verbose_name="Contact Number", null=True)

    objects = CustomUserManager()

    def get_name(self):
        return "{} {}".format(self.first_name, self.last_name)

    def has_perm(self, perm, obj=None):
        """Does the user have a specific permission?"""
        return True

    def has_module_perms(self, app_label):
        """Does the user have permissions to view the app `app_label`?"""
        return True

    @property
    def is_staff(self):
        """Is the user a member of staff?"""
        return self.is_admin

    def __str__(self):
        return "{} {}".format(self.first_name, self.last_name)


class Commute(models.Model):
    user = models.ForeignKey(User, null=False, blank=False, related_name='hosts_trip', on_delete=models.CASCADE)
    time = models.DateTimeField(verbose_name='Time of Commute', blank=False, null=False)
    start_latitude = models.FloatField(verbose_name="Starting Place Latitude", null=False, blank=True)
    start_longitude = models.FloatField(verbose_name="Starting Place Longitude", null=False, blank=True)
    start_name = models.TextField(verbose_name="Starting Place", null=False, blank=True)
    end_latitude = models.FloatField(verbose_name="Ending Place Latitude", null=False, blank=True)
    end_longitude = models.FloatField(verbose_name="Ending Place Longitude", null=False, blank=True)
    end_name = models.TextField(verbose_name="Ending Place Name", null=False, blank=True)
    seats = models.IntegerField()
    participants = models.ManyToManyField(User, related_name='trips', blank=True)

    def __str__(self):
        return "{} to {} at {}".format(self.start_name, self.end_name, self.format_time())

    def to_json(self):
        """JSON."""
        return {
            "id": self.id,
            "time": self.format_time(),
            "email": self.user.email,
            "contact_number": self.user.contact_number if self.user.contact_number else "",
            "seats": self.seats,
        }

    def format_time(self):
        """Format the time the European way."""
        return self.time.strftime("%d/%m/%Y %H:%M")
