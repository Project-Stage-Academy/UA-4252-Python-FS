from rest_framework import serializers

from .models import StartupProfile


class StartupPublicProfileSerializer(serializers.ModelSerializer):
    logo_url = serializers.SerializerMethodField()
    partners_brands = serializers.SerializerMethodField()
    followers_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = StartupProfile
        fields = [
            "id",
            "company_name",
            "description",
            "founded_year",
            "team_size",
            "website",
            "email",
            "phone",
            "city",
            "logo_url",
            "tags",
            "partners_brands",
            "followers_count",
            "created_at",
            "updated_at",
        ]

    def get_logo_url(self, obj):
        request = self.context.get("request")
        if obj.logo and hasattr(obj.logo, "url"):
            return request.build_absolute_uri(obj.logo.url)
        return None

    def get_partners_brands(self, obj):
        if obj.partners_brands:
            return [
                partner.strip()
                for partner in obj.partners_brands.split(",")
                if partner.strip()
            ]
        return []
