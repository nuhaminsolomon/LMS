from datetime import datetime
from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Book, Transaction
from .serializers import BookSerializer, TransactionSerializer
from rest_framework.pagination import PageNumberPagination

class CustomPagination(PageNumberPagination):
    page_size = 2
    page_size_query_param = 'page_size'  
    max_page_size = 2

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    pagination_class = CustomPagination

class TransactionViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def checkout(self, request, pk=None):
        book = Book.objects.get(pk=pk)
        if book.copies_available > 0:
            transaction = Transaction.objects.create(user=request.user, book=book)
            book.copies_available -= 1
            book.save()
            return Response(TransactionSerializer(transaction).data, status=status.HTTP_201_CREATED)
        return Response({"error": "No copies available"}, status=status.HTTP_400_BAD_REQUEST)

    def return_book(self, request, pk=None):
        transaction = Transaction.objects.get(pk=pk, user=request.user)
        transaction.return_date = datetime.now()
        transaction.save()
        book = transaction.book
        book.copies_available += 1
        book.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def my_history(self, request):
        res=Transaction.objects.filter(user=request.user)
        Serializer = TransactionSerializer(res,many=True )
        return Response(Serializer.data,status=status.HTTP_200_OK)
    

