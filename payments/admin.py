from django.contrib import admin
from .models import *

admin.site.register(Transaction)
admin.site.register(AccountEntry)
admin.site.register(Expense)
admin.site.register(SalaryEntry)
