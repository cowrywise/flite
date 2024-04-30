# Flite

#TODO: update readme for local development 
I need robust tests, i currently have this packages 
# Testing
mock==2.0.0
factory-boy==2.11.1
django-nose==1.4.6
nose-progressive==1.5.2
coverage==4.5.2

# Create your views here.
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import BudgetCategory, Transaction
from .serializers import BudgetCategorySerializer, TransactionSerializer

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def budget_category_list(request):
    if request.method == 'GET':
        categories = BudgetCategory.objects.all()
        serializer = BudgetCategorySerializer(categories, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = BudgetCategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def budget_category_detail(request, pk):
    try:
        category = BudgetCategory.objects.get(pk=pk)
    except BudgetCategory.DoesNotExist:
        return Response(status=404)

    if request.method == 'GET':
        serializer = BudgetCategorySerializer(category)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = BudgetCategorySerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    elif request.method == 'DELETE':
        category.delete()
        return Response(status=204)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def transaction_list(request):
    if request.method == 'GET':
        transactions = Transaction.objects.filter(owner=request.user)
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = TransactionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(owner=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def transaction_detail(request, pk):
    try:
        transaction = Transaction.objects.get(pk=pk, owner=request.user)
    except Transaction.DoesNotExist:
        return Response(status=404)

    if request.method == 'GET':
        serializer = TransactionSerializer(transaction)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = TransactionSerializer(transaction, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    elif request.method == 'DELETE':
        transaction.delete()
        return Response(status=204)

# Create your models here.
import uuid
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

from django.conf import settings
class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created = models.DateTimeField(default=timezone.now, editable=False)
    modified = models.DateTimeField(auto_now=True, blank=True, null=True)

    class Meta:
        abstract = True

class BudgetCategory(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    max_spend = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return self.name

class Transaction(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,related_name='transactions')
    # other fields...
    category = models.ForeignKey(BudgetCategory, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.category.name} - {self.amount}"

 #### tasks.py 
from celery import shared_task
from django.core.mail import send_mail
from .models import BudgetCategory, Transaction

@shared_task
def check_budget_threshold():
    for category in BudgetCategory.objects.all():
        total_spend = Transaction.objects.filter(category=category).aggregate(Sum('amount'))['amount__sum']
        if total_spend >= category.max_spend * 0.5:
            send_mail(
                'Budget threshold warning',
                f'Your spending for {category.name} has reached {total_spend}, which is over 50% of your budget.',
                'from@example.com',
                [category.owner.email],
                fail_silently=False,
            )