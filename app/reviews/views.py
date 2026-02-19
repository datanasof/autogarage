from rest_framework import generics, permissions
from .models import Review
from .serializers import ReviewSerializer
class ReviewCreateView(generics.CreateAPIView): queryset=Review.objects.all(); serializer_class=ReviewSerializer; permission_classes=[permissions.IsAuthenticated]
