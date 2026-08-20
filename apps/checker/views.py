import os

from django.shortcuts import render
from django.http import JsonResponse
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import OpenApiTypes, extend_schema

from .models import OcrSchemaRecord

# Create your views here.

def home(request):
    return JsonResponse(
        {
            'hello': 'this is home'
        },
        status=200   #status=status.HTTP_200_OK
    )


class BankOcrRequestSerializer(serializers.Serializer):
    image_path = serializers.CharField(help_text="Path to the bank document image")


class BankOcrView(APIView):
    @extend_schema(
        request=BankOcrRequestSerializer,
        responses={200: OpenApiTypes.OBJECT},
    )
    def post(self, request):
        image_path = request.data.get("image_path")

        if not image_path:
            return Response(
                {"error": "image_path is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not os.path.exists(image_path):
            return Response(
                {"error": f"image not found at {image_path}"},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            from .bank_ocr import analyze_image
        except ValueError as exc:
            return Response(
                {"error": str(exc)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        try:
            result = analyze_image(image_path)
        except Exception as exc:
            return Response(
                {"error": str(exc)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(result.model_dump(), status=status.HTTP_200_OK)


class SchemaRecordSerializer(serializers.Serializer):
    schema_data = serializers.JSONField(help_text="Schema payload to store as-is")


class SchemaRecordView(APIView):
    @extend_schema(
        request=SchemaRecordSerializer,
        responses={201: OpenApiTypes.OBJECT},
    )
    def post(self, request):
        serializer = SchemaRecordSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        record = OcrSchemaRecord.objects.create(
            schema_data=serializer.validated_data["schema_data"]
        )

        return Response(
            {
                "id": record.pk,
                "schema_data": record.schema_data,
                "created_at": record.created_at,
            },
            status=status.HTTP_201_CREATED,
        )