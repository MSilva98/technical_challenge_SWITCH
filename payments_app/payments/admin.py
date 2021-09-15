from django.contrib import admin

from .models import Base, CreditCard, MbWay

# Register your models here.
admin.site.register(Base)
admin.site.register(CreditCard)
admin.site.register(MbWay)
