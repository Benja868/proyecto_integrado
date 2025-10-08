from django.contrib import admin
from .models import Organization, Zone, Device, Measurement

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
    list_display = ("name", "organization")
    search_fields = ("name", "organization__name")
    list_filter = ("organization",)
    ordering = ("organization", "name")
    list_select_related = ("organization",)


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ("name", "zone", "serial")
    search_fields = ("name", "serial", "zone__name", "zone__organization__name")
    list_filter = ("zone__organization", "zone")
    ordering = ("zone__organization", "zone", "name")
    list_select_related = ("zone", "zone__organization")


@admin.register(Measurement)
class MeasurementAdmin(admin.ModelAdmin):
    list_display = ("device", "value", "created_at")
    search_fields = ("device__name", "device__serial", "device__zone__name")
    list_filter = ("device__zone__organization", "device__zone")
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    list_select_related = ("device", "device__zone", "device__zone__organization")
