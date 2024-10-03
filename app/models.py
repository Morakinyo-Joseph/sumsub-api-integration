from django.db import models


class Applicant(models.Model):
    external_user_id = models.CharField(max_length=50)
    applicant_id = models.CharField(max_length=50, null=True)
    country = models.CharField(max_length=3, null=True)
    id_doc_type = models.CharField(max_length=20, null=True)
    image_id = models.CharField(max_length=255, null=True)
    review_result = models.JSONField(null=True) 