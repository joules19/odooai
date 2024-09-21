from django.urls import path, include

from .views import CVExtractorView, EvaluateResumeView, GenerateCoverLetterView

urlpatterns = [
    path('extract-info/', CVExtractorView.as_view(), name='extract_info'),
    path('analyze-resume/', EvaluateResumeView.as_view(), name='analyze-resume'),
    path('generate-cv/', GenerateCoverLetterView.as_view(), name='generate-cv'),
    # path('google-profile-image/', GoogleProfileImageView.as_view(), name='google_profile_image'),
]
