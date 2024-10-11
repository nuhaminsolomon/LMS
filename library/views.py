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
from rest_framework.decorators import action


class CustomPagination(PageNumberPagination):
    page_size = 2
    page_size_query_param = 'page_size'  
    max_page_size = 2

import django_filters
from .models import Book

class BookFilter(filters.FilterSet):
    title = filters.CharFilter(lookup_expr='icontains')
    author = filters.CharFilter(lookup_expr='icontains')
    isbn = filters.CharFilter(lookup_expr='exact')

    class Meta:
        model = Book
        fields = ['title', 'author', 'isbn']

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    pagination_class = CustomPagination
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = BookFilter
    
    @action(detail=False, methods=['get'], url_path='available')
    def list_available_books(self, request):
        # Filter books where copies_available is greater than 0
        available_books = Book.objects.filter(copies_available__gt=0)

        # Apply filters if they are present in the request
        filtered_books = self.filter_queryset(available_books)

        # Paginate the filtered available books
        page = self.paginate_queryset(filtered_books)
        if page is not None:
            serializer = BookSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        # If no pagination was applied, return all available books
        serializer = BookSerializer(filtered_books, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

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
    
    def list_available_books(self, request):
        res=Book.objects.filter(copies_available__gt = 0)
        Serializer = BookSerializer(res,many=True )
        return Response(Serializer.data,status=status.HTTP_200_OK)
    

