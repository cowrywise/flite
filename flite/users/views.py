from rest_framework import viewsets, mixins
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import User, NewUserPhoneVerification
from .permissions import IsUserOrReadOnly
from .serializers import CreateUserSerializer, UserSerializer, SendNewPhonenumberSerializer, DepositSerializer
from rest_framework.views import APIView
from . import utils
from .utils import deposit_transaction


class UserViewSet(mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  viewsets.GenericViewSet):
    """
    Updates and retrieves user accounts
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsUserOrReadOnly,)


class UserCreateViewSet(mixins.CreateModelMixin,
                        viewsets.GenericViewSet):
    """
    Creates user accounts
    """
    queryset = User.objects.all()
    serializer_class = CreateUserSerializer
    permission_classes = (AllowAny,)


class SendNewPhonenumberVerifyViewSet(mixins.CreateModelMixin,mixins.UpdateModelMixin, viewsets.GenericViewSet):
    """
    Sending of verification code
    """
    queryset = NewUserPhoneVerification.objects.all()
    serializer_class = SendNewPhonenumberSerializer
    permission_classes = (AllowAny,)


    def update(self, request, pk=None,**kwargs):
        verification_object = self.get_object()
        code = request.data.get("code")

        if code is None:
            return Response({"message":"Request not successful"}, 400)    

        if verification_object.verification_code != code:
            return Response({"message":"Verification code is incorrect"}, 400)    

        code_status, msg = utils.validate_mobile_signup_sms(verification_object.phone_number, code)
        
        content = {
                'verification_code_status': str(code_status),
                'message': msg,
        }
        return Response(content, 200)


@api_view(['GET'])
def get_user_list(request, user_id):
    user = User.objects.filter(id=user_id).first()
    content = {
        'data': UserSerializer(user).data
    }
    return Response(content, status=status.HTTP_200_OK)


@api_view(['POST'])
def deposit_account(request, user_id):
    data = request.data
    serializer = DepositSerializer(data=data)
    if serializer.is_valid():
        amount = serializer.validated_data.get('amount')
        user = User.objects.filter(id=user_id).first()
        if user:
            deposit_transaction(user, amount)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"error": "User not found"}, status=status.HTTP_400_OK)
    else:
        return Response({"error": serializer.errors}, status=status.HTTP_400_OK)


