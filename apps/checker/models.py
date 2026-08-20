from django.db import models


class OcrSchemaRecord(models.Model):
    schema_data = models.JSONField(help_text="OCR schema payload stored as JSON")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"OcrSchemaRecord #{self.pk} ({self.created_at})"
