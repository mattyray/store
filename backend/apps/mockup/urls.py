from django.urls import path
from . import views

app_name = 'mockup'

urlpatterns = [
    # Wall analysis
    path('analyze/', views.UploadWallImageView.as_view(), name='upload'),
    path('analyze/<uuid:analysis_id>/', views.WallAnalysisDetailView.as_view(), name='analysis-detail'),

    # Save/retrieve mockups
    path('save/', views.SaveMockupView.as_view(), name='save'),
    path('<uuid:mockup_id>/', views.MockupDetailView.as_view(), name='mockup-detail'),
]
