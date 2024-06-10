from rest_framework import viewsets
from rest_framework.response import Response
from .serializer import DeliverySerializer
from .models import Delivery

class DeliveryViewSet(viewsets.ModelViewSet):
    queryset = Delivery.objects.all()
    serializer_class = DeliverySerializer
