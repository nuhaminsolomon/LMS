from datetime import datetime
from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Book, Transaction
from .serializers import BookSerializer, TransactionSerializer
from rest_framework.pagination import PageNumberPagination
from django_filters import rest_framework as filters

class CustomPagination(PageNumberPagination):
    page_size = 2
    page_size_query_param = 'page_size'  
    max_page_size = 2

import django_filters
from .models import Book

class BookFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains')
    author = django_filters.CharFilter(lookup_expr='icontains')
    isbn = django_filters.CharFilter(lookup_expr='exact')  # Exact match for ISBN
    published_date = django_filters.DateFilter()
    copies_available = django_filters.NumberFilter()  # For filtering by number of copies

    class Meta:
        model = Book
        fields = ['title', 'author', 'isbn', 'published_date', 'copies_available']

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    pagination_class = CustomPagination
    # filter_backends = (filters.DjangoFilterBackend,)
    # filterset_class = BookFilter
    

class TransactionViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def checkout(self, request, pk=None):
        book = Book.objects.get(pk=pk)
        if book.copies_available > 0:
            transactions = Transaction.objects.filter(book=book, user=request.user)

            # Check if there are any transactions and if the return date is None
            if transactions.exists() and transactions.filter(return_date__isnull=True).exists():
                return Response({"error": "already borrowed"}, status=status.HTTP_403_FORBIDDEN)

            transaction = Transaction.objects.create(user=request.user, book=book)
            book.copies_available -= 1
            book.save()
            return Response(TransactionSerializer(transaction).data, status=status.HTTP_201_CREATED)
        return Response({"error": "No copies available"}, status=status.HTTP_400_BAD_REQUEST)

    def return_book(self, request, pk=None):
        transaction = Transaction.objects.get(pk=pk, user=request.user)
        if transaction.return_date!=None:
            return Response({"error":"already returned"}, status=status.HTTP_403_FORBIDDEN)

        transaction.return_date = datetime.now()
        transaction.save()
        book = transaction.book
        book.copies_available += 1
        book.save()
        return Response({"success":"Book returned successfully"}, status=status.HTTP_204_NO_CONTENT)
    
    def my_history(self, request):
        res=Transaction.objects.filter(user=request.user)
        Serializer = TransactionSerializer(res,many=True )
        return Response(Serializer.data,status=status.HTTP_200_OK)
    

