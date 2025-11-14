import uuid
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Interest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    investor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="expressed_interests"
    )

    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        related_name="expressed_interests"
    )

    message = models.TextField(blank=True, null=True)

    contact_opt_in = models.BooleanField(default=False)

    status = models.CharField(
        max_length=32,
        default="expressed",
        choices=[
            ("expressed", "Expressed"),
            ("contacted", "Contacted"),
            ("ignored", "Ignored"),
        ]
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Interest {self.id} by {self.investor_id}"
