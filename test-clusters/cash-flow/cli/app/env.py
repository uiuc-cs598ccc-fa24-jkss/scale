import os


def setup_api(env):
    if env == 'kube':
        from cli.app.k8s import commands as k8s_commands
        os.environ['AUTH_API_URL'] = k8s_commands.get_service_ip('auth')
        os.environ['DMS_API_URL'] = k8s_commands.get_service_ip('dms')
        os.environ['REGISTRATION_API_URL'] = k8s_commands.get_service_ip('registration')
        os.environ['TASKING_API_URL'] = k8s_commands.get_service_ip('tasking')
        os.environ['TRANSACTION_API_URL'] = k8s_commands.get_service_ip('transaction')
        os.environ['REDIS_URL'] = k8s_commands.get_service_ip('redis') 
    elif env == 'docker':
        os.environ['REDIS_URL'] = 'http://localhost:6379'