from server.models.notification_response import NotificationResponse
from server.models.password_reset_code_notification_request import PasswordResetCodeNotificationRequest
from server.models.verification_code_notification_request import VerificationCodeNotificationRequest
from server.models.welcome_email_notification_request import WelcomeEmailNotificationRequest

from server.apis.default_api_base import BaseDefaultApi

from app_logging import AppLogger, config

logger = AppLogger('NotificationService')

class NotificationService(BaseDefaultApi):
    
    async def send_password_reset_code_notification(
        self,
        request: PasswordResetCodeNotificationRequest,
    ) -> NotificationResponse:
        logger.debug(f'Sending password reset code {request.reset_code} to email: {request.user_email}')
        return NotificationResponse(status='success', message='Password reset code sent successfully')

    async def send_verification_code_notification(
        self,
        request: VerificationCodeNotificationRequest,
    ) -> NotificationResponse:
        logger.debug(f'Sending verification code {request.verification_code} to email: {request.user_email}')
        return NotificationResponse(status='success', message='Verification code sent successfully')

    async def send_welcome_email_notification(
        self,
        request: WelcomeEmailNotificationRequest,
    ) -> NotificationResponse:
        logger.debug(f'Sending welcome email to email: {request.user_email}')
        return NotificationResponse(status='success', message='Welcome email sent successfully')