from rest_framework import serializers

class UploadPdfSerializer(serializers.Serializer):
    files = serializers.ListField(child=serializers.FileField(), allow_empty=False)

class AskSerializer(serializers.Serializer):
    question = serializers.CharField(max_length=2000)
