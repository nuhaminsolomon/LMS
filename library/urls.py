from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BookViewSet, TransactionViewSet

router = DefaultRouter()
router.register(r'books', BookViewSet)
router.register(r'transactions', TransactionViewSet, basename='transaction')

urlpatterns = [
    path('', include(router.urls)),
    path('checkout/<int:pk>/', TransactionViewSet.as_view({'post': 'checkout'}), name='checkout'),
    path('return/<int:pk>/', TransactionViewSet.as_view({'post': 'return_book'}), name='return_book'),
    path('my_history', TransactionViewSet.as_view({'get': 'my_history'}),name='my_history'),
]
