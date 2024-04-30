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