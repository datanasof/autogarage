from rest_framework import serializers
from .models import Review
class ReviewSerializer(serializers.ModelSerializer):
    class Meta: model=Review; fields=("id","appointment","provider","user","rating","comment"); read_only_fields=("user",)
    def validate(self, attrs): attrs["user"]=self.context["request"].user; return attrs
