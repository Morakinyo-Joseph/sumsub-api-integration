from django.shortcuts import render
from django.conf import settings
from django.shortcuts import get_object_or_404
from .models import Applicant
from .utils import get_auth_headers, decode_base64_image, auto_generate
from rest_framework.decorators import APIView
from rest_framework.response import Response
import requests
import uuid
import os
import base64
import json

class SumsubApplicant(APIView):
    def post(self, request):
        external_user_id = uuid.uuid4()
        level_name = request.data["levelName"]

        # To track the applicant data
        new_applicant = Applicant.objects.create(external_user_id=external_user_id)
        new_applicant.save()

        url = f"{settings.SUMSUB_BASE_URL}/resources/applicants?levelName={level_name}"
        data = {
            "externalUserId": str(external_user_id)
        }
        headers = get_auth_headers(url, method="POST", body=json.dumps(data))

        response = requests.post(url=url, headers=headers, json=data)

        # save applicant_id 
        if response.status_code == 201:
            data = response.json()
            new_applicant.applicant_id = data["id"]
            new_applicant.save()

        return Response(response.json())
    

class SumsubDocument(APIView):
    def post(self, request, applicant_id):
        file = request.data["image_file"] #base64 image format

        # decode base64 iamge
        file = str(file).encode('ascii')
        file = decode_base64_image(file)

        file_path = auto_generate(12)
        save_path = os.path.join(settings.MEDIA_ROOT, f"{file_path}.png")

        with open(save_path, "wb") as sample:
            sample.write(base64.decodebytes(file))

        with open(save_path, 'rb') as img_file:
            files = {'content': img_file}
            payload = {"metadata": f'{request.data["meta_data"]}'}

            url = f"{settings.SUMSUB_BASE_URL}/resources/applicants/{applicant_id}/info/idDoc"
            
            headers = get_auth_headers(url, method="POST", body=payload)
            headers["X-Return-Doc-Warnings"] = "true"

            response = requests.post(url, headers=headers, data=payload, files=files)

        return Response(response.json())




class SumsubStatusView(APIView):
    def get(self, request, applicant_id):
        url = f"{settings.SUMSUB_BASE_URL}/resources/applicants/{applicant_id}/requiredIdDocsStatus"
        headers = get_auth_headers(url, method="GET")

        response = requests.get(url, headers=headers)

        if response.status_code == 200 and response.json()['IDENTITY'] !=  None:
            data = response.json()

            # Extract relevant information from the response
            identity_info = data["IDENTITY"]
            country = identity_info['country']
            id_doc_type = identity_info['idDocType']
            image_ids = identity_info.get('imageIds', [])
            review_result = identity_info['reviewResult']

            applicant = get_object_or_404(Applicant, applicant_id=applicant_id)
            applicant.country = country
            applicant.id_doc_type = id_doc_type
            applicant.image_id = image_ids[0] if image_ids else None
            applicant.review_result = review_result
            applicant.save()


        return Response(response.json())
