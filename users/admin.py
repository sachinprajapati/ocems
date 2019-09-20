from django.contrib import admin

from .models import *

@admin.register(Flats)
class FlatsAdmin(admin.ModelAdmin):
    ordering = ['tower', 'flat']
    search_fields = ['tower', 'flat']


#admin.site.register(FlatsAdmin)
