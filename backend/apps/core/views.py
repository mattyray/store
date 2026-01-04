from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.orders.emails import send_contact_form_notification


class ContactFormView(APIView):
    """Handle contact form submissions."""

    def post(self, request):
        name = request.data.get('name', '').strip()
        email = request.data.get('email', '').strip()
        subject = request.data.get('subject', '').strip()
        message = request.data.get('message', '').strip()

        if not all([name, email, message]):
            return Response(
                {'error': 'Name, email, and message are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not subject:
            subject = 'General Inquiry'

        try:
            send_contact_form_notification(name, email, subject, message)
            return Response({'success': True, 'message': 'Message sent successfully'})
        except Exception as e:
            return Response(
                {'error': 'Failed to send message. Please try again.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class HealthCheckView(APIView):
    """Simple health check endpoint."""

    def get(self, request):
        return Response({'status': 'ok'})
