from django.http import JsonResponse, HttpResponse
from rest_framework.decorators import api_view
import requests
import os
from django.conf import settings
from apps.general.models import InvoiceComparison
from .utils import save_pdf_temporarily, get_existing_pdf, cleanup_old_pdfs

@api_view(['GET'])
def download_report(request):
    try:
        # Obtener el ID de comparación
        comparison_id = request.query_params.get('id')
        if not comparison_id:
            return JsonResponse({"error": "Comparison ID is required."}, status=400)

        # Buscar el objeto de comparación
        comparison = InvoiceComparison.objects.filter(id=comparison_id, user=request.user).first()
        if not comparison:
            return JsonResponse({"error": "No comparison data found for the provided ID."}, status=404)

        # Verificar si ya existe un PDF para el usuario y la comparación
        existing_pdf_path = get_existing_pdf(request.user.id, comparison_id)
        if existing_pdf_path:
            # Si el archivo existe y no ha expirado, devolverlo
            with open(existing_pdf_path, 'rb') as f:
                pdf = f.read()
            return HttpResponse(pdf, content_type="application/pdf")

        # Preparar datos para el microservicio
        comparison_data = {
            "user": request.user.fullname,
            "billing_period_start": comparison.invoice.billing_period_start.isoformat(),
            "billing_period_end": comparison.invoice.billing_period_end.isoformat(),
            "measurement_start": comparison.measurement.measurement_start.isoformat(),
            "measurement_end": comparison.measurement.measurement_end.isoformat(),
            "comparison_results": comparison.comparison_results,
            "is_comparison_valid": comparison.is_comparison_valid,
        }

        # Hacer la solicitud al microservicio
        microservice_url = "http://127.0.0.1:8002/download_report"
        response = requests.post(microservice_url, json=comparison_data)

        # Si la solicitud al microservicio fue exitosa
        if response.status_code == 200:
            pdf_data = response.content

            # Guardar el PDF de forma temporal
            pdf_path = save_pdf_temporarily(pdf_data, request.user.id, comparison_id)

            # Devolver el archivo al cliente
            with open(pdf_path, 'rb') as f:
                pdf = f.read()
            return HttpResponse(pdf, content_type="application/pdf")
        else:
            return JsonResponse({"error": "Failed to generate PDF."}, status=500)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
