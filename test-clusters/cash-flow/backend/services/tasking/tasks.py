import os
from celery_config import app
import interfaces.internal.dms.dms_client as dms_client
import interfaces.internal.notification.notification_client as notif_client
from interfaces.internal.notification.notification_client.models import VerificationCodeNotificationRequest

# import DefaultApi, TransactionCreate, Configuration, ApiClient

import tasks

dms_config = dms_client.Configuration()
dms_config.host = os.getenv('DMS_API_URL', 'http://localhost:8080')
dms_api = dms_client.DefaultApi(dms_client.ApiClient(dms_config))

notif_config = notif_client.Configuration()
notif_config.host = os.getenv('NOTIF_API_URL', 'http://localhost:8080')
notif_api = notif_client.DefaultApi(notif_client.ApiClient(notif_config))

@app.task(name='generic.call_service')
def call_service(service_name: str, method_name: str, *args, **kwargs):
    """
    Call a service method in the background.
    """
    print(f'Calling service: {service_name}.{method_name}')
    service = getattr(tasks, service_name)
    method = getattr(service, method_name)
    return method(*args, **kwargs)

@app.task
def send_welcome_email(user_email):
    print(f"Sending welcome email to {user_email}")
    try:
        response = notif_api.send_welcome_email_notification(
            {
                'user_email': user_email,
                'message': 'Welcome to our cash-flow',
            } 
        )
        return {'status': 'success'}
    except Exception as e:
        print(f'Welcome email failed with error: {e}')
        return {"status": "failed", "error": str(e)}
        
@app.task
def send_registration_code_email(email, code):

    try: 
        response = notif_api.send_verification_code_notification(
            VerificationCodeNotificationRequest(user_email=email, verification_code=code)
        )

        return {'status': 'success'}
    except Exception as e:
        print(f'Registration code email failed with error: {e}')
        return {"status": "failed", "error": str(e)}
    

@app.task
def process_enrollment(user_data: dict):
    """
    Create a user in the background.
    """
    print ('processing enrollment')


@app.task
def process_transaction(transaction_data: dict):
    """
    Process a transaction in the background.
    """
    print (f'processing transaction: {transaction_data}')
   
    try:
        print(f'Calling DMS for transaction upload request: {transaction_data}')
        response = dms_api.create_transaction(transaction_data['transaction'])
        print (f'DMS response: {response}')
        print (f'response type: {type(response)}')
        return {'status': 'success'}
        # return response
        # print (f'response type: type(response)')
    except Exception as e:
        print(f'Transaction upload failed with error: {e}')
        return {"status": "failed", "error": str(e)}


@app.task
def process_bulk_transactions(
    transaction_dict: dict):
    """
    Process multiple transactions in the background.
    """
    print('Processing bulk transactions task')
    print(f'Transactions: {transaction_dict}')

    try:
        # Access the list of transactions from the transaction_dict
        transactions_data = transaction_dict.get('transactions_data', [])
        
        # Create Transaction objects from the list of dictionaries
        transactions = [TransactionCreate(**transaction_data) for transaction_data in transactions_data]

        print(f'Calling DMS for bulk transaction upload request: {transactions}')
        dms_api.add_transactions(transactions)
        return {"status": "success"}

    except Exception as e:
        print(f'Bulk transaction upload failed with error: {e}')
        return {"status": "failed", "error": str(e)}
 