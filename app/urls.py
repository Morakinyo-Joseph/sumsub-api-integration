from django.urls import path
from .views import *

urlpatterns = [
    path("applicant", SumsubApplicant.as_view(), name="create-applicant"),
    path("applicant/<str:applicant_id>/document", SumsubDocument.as_view(), name="upload-document"),
    path("applicant/<str:applicant_id>/status", SumsubStatusView.as_view(), name="status-verify"),
]