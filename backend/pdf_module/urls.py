
from django.urls import path
from . import views
urlpatterns = [
    path('',views.pdf_files,name="pdf_routes"),
    path('<str:pk>',views.get_pdf,name="get_pdf"),
    path('post_pdf/post',views.post_pdf,name="post_pdf"),
    path('get_pdf/analyzed_pdf',views.getAnalyzedPdf,name="analyzed_pdf"),
    path('analyzed-conveyance/<str:pk>/', views.analyzed_conveyance_detail, name='analyzed-conveyance-detail'),
]
