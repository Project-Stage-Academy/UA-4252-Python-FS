from rest_framework import serializers
from .models import StartupProfile

class StartupPublicProfileSerializer(serializers.ModelSerializer):
    logo_url = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    followers_count = serializers.SerializerMethodField()

    class Meta:
        model = StartupProfile
        fields = [
            'id',
            'company_name',
            'description',
            'founded_year',
            'team_size',
            'website',
            'email',
            'phone',
            'city',
            'logo_url',
            'tags',
            'followers_count',
            'created_at',
        ]

    def get_logo_url(self, obj):
        request = self.context.get('request')
        if obj.logo and hasattr(obj.logo, 'url'):
            return request.build_absolute_uri(obj.logo.url)
        return None

    def get_tags(self, obj):
        if obj.partners_brands:
            return [tag.strip() for tag in obj.partners_brands.split(',') if tag.strip()]
        return []

    def get_followers_count(self, obj):
        val = getattr(obj, "followers_count", None)
        if val is not None:
            try:
                return int(val)
            except Exception:
                pass

        for rel in ("followers", "followers_set", "investor_followers"):
            rel_obj = getattr(obj, rel, None)
            if rel_obj is not None and hasattr(rel_obj, "count"):
                try:
                    return int(rel_obj.count())
                except Exception:
                    break
        return 0