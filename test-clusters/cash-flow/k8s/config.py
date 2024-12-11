import os
from dotenv import dotenv_values
from dataclasses import dataclass

env = dotenv_values('.env')

@dataclass
class TemplateConfig:
    """
    Represents the configuration for a template.

    Attributes:
        service_name (str): The name of the service.
        namespace (str): The namespace of the service.
        config (dict, optional): The configuration data.
        secrets (dict, optional): The secrets data.
    """
    service_name: str
    namespace: str
    config: dict = None
    secrets: dict = None

    def get_config_data(self):
        """
        Returns the configuration data.

        Returns:
            dict: The configuration data.
        """
        if self.config:
            return {
                "service_name": self.service_name,
                "namespace": self.namespace,
                "data": self.config
            }
    
    def get_secrets_data(self):
        """
        Returns the secrets data.

        Returns:
            dict: The secrets data.
        """
        if self.secrets:
            return {
                "service_name": self.service_name,
                "namespace": self.namespace,
                "data": self.secrets
            }

template_configs = [
    # Auth service
    TemplateConfig(
        service_name="auth",
        namespace="cash-flow",
        config={
            "TASKING_API_URL": env["TASKING_API_URL"],
            "USER_DB_HOST": env["USER_DB_HOST"],
            "USER_DB_PORT": env["USER_DB_PORT"],
            "USER_DB_USER": env["USER_DB_USER"],
            "USER_DB_DB": env["USER_DB_DB"],
            "USER_DB_HOST_PORT": env["USER_DB_HOST_PORT"]
        },
        secrets={
            "USER_DB_PASSWORD": env["USER_DB_PASSWORD"],
            "JWT_ALGORITHM": env["JWT_ALGORITHM"],
            "JWT_SECRET_KEY": env["JWT_SECRET_KEY"],
            "JWT_EXPIRATION": env["JWT_EXPIRATION"]
        }
    ),
    
    # Celery service
    TemplateConfig(
        service_name="celery",
        namespace="cash-flow",
        config={
            "REDIS_URL": env["REDIS_URL"],
            "DMS_API_URL": env["DMS_API_URL"],
            "NOTIF_API_URL": env["NOTIF_API_URL"],
        }
    ),

    # DMS service
    TemplateConfig(
        service_name="dms",
        namespace="cash-flow",
        config={
            "REDIS_URL": env["REDIS_URL"],
            "TX_DB_HOST": env["TX_DB_HOST"],
            "TX_DB_PORT": env["TX_DB_PORT"],
            "TX_DB_USER": env["TX_DB_USER"],
            "TX_DB_DB": env["TX_DB_DB"],
            "TX_DB_HOST_PORT": env["TX_DB_HOST_PORT"]
        },
        secrets={
            "TX_DB_PASSWORD": env["TX_DB_PASSWORD"],
        }
    ),

    # Registration service
    TemplateConfig(
        service_name="registration",
        namespace="cash-flow",
        config={
            "AUTH_API_URL": env["AUTH_API_URL"],
            "TASKING_API_URL": env["TASKING_API_URL"],
        }
    ),

    TemplateConfig(
        service_name="tasking",
        namespace="cash-flow",
        config={
            "DMS_API_URL": env["DMS_API_URL"],
            "NOTIF_API_URL": env["NOTIF_API_URL"],
        }
    ),

    TemplateConfig(
        service_name="transaction",
        namespace="cash-flow",
        config={
            "AUTH_API_URL": env["AUTH_API_URL"],
            "DMS_API_URL": env["DMS_API_URL"],
            "TASKING_API_URL": env["TASKING_API_URL"],
        }
    ),

    TemplateConfig(
        service_name="tx-db",
        namespace="cash-flow",
        config={
            "POSTGRES_DB": env["TX_DB_DB"],
            "POSTGRES_USER": env["TX_DB_USER"],
        },
        secrets={
            "POSTGRES_PASSWORD": env["TX_DB_PASSWORD"],
        }
    ),

    TemplateConfig(
        service_name="user-db",
        namespace="cash-flow",
        config={
            "POSTGRES_DB": env["USER_DB_DB"],
            "POSTGRES_USER": env["USER_DB_USER"],
        },
        secrets={
            "POSTGRES_PASSWORD": env["USER_DB_PASSWORD"],
        }
    ),
]

# auth_config = {
#     "service_name": "auth",
#     "namespace": "cash-flow",

#     "config": {
#         "data": {        
#             "TASKING_API_URL": env["TASKING_API_URL"],
#             "USER_DB_HOST": env["USER_DB_HOST"],
#             "USER_DB_PORT": env["USER_DB_PORT"],
#             "USER_DB_USER": env["USER_DB_USER"],
#             "USER_DB_DATABASE": env["USER_DB_DB"]
#         }
#     }, 

#     "secrets": {
#         "data": {
#             "USER_DB_PASSWORD": env["USER_DB_PASSWORD"],
#             "JWT_ALGORITHM": env["JWT_ALGORITHM"],
#             "JWT_SECRET_KEY": env["JWT_SECRET_KEY"],
#             "JWT_EXPIRATION": env["JWT_EXPIRATION"]
#         }
#     },
# }

# celery_config = {
#     "service_name": "celery",
#     "namespace": "cash-flow",
#     "config": {
#         "data": {
#             "REDIS_URL": env["REDIS_URL"],
#             "DMS_API_URL": env["DMS_API_URL"],
#         }
#     }
# }

# dms_config = {
#     "service_name": "dms",
#     "namespace": "cash-flow",

#     "config": {
#         "data": {
#             "REDIS_URL": env["REDIS_URL"],
#             "TX_DB_HOST": env["TX_DB_HOST"],
#             "TX_DB_PORT": env["TX_DB_PORT"],
#             "TX_DB_USER": env["TX_DB_USER"],
#         }
#     },

#     "secrets": {
#         "data": {
#             "TX_DB_PASSWORD": env["TX_DB_PASSWORD"],
#         }
#     }
# }

# registration_config = {
#     "service_name": "registration",
#     "namespace": "cash-flow",
    
#     "config": {
#         "data": {
#             "AUTH_API_URL": env["AUTH_API_URL"],
#             "TASKING_API_URL": env["TASKING_API_URL"],
#         }
#     },
#     # "secrets": {
#     #     "data": {
#     #     }
#     # },
# }

# # tasking_config = {
# #     "service_name": "tasking",
# #     "namespace": "cash-flow",
    
# #     "config": {
# #         "data": {

# #         }
# #     },
# #     "secrets": {
# #         "data": {
# #         }
# #     },
# # }

# transaction_config = {
#     "service_name": "transaction",
#     "namespace": "cash-flow",
    
#     "config": {
#         "data": {
#             "AUTH_API_URL": env["AUTH_API_URL"],
#             "DMS_API_URL": env["DMS_API_URL"],
#             "TASKING_API_URL": env["TASKING_API_URL"],
#         }
#     },
#     # "secrets": {
#     #     "data": {
#     #     }
#     # },
# }

# tx_db_config = {
#     "service_name": "tx_db",
#     "namespace": "cash-flow",
    
#     "config": {
#         "data": {
#             "POSTGRES_DB": env["TX_DB_DB"],
#             "POSTGRES_USER": env["TX_DB_USER"],
#         }
#     },
#     "secrets": {
#         "data": {
#             "POSTGRES_PASSWORD": env["TX_DB_PASSWORD"],
#         }
#     },
# }

# user_db_config = {
#     "service_name": "user_db",
#     "namespace": "cash-flow",
    
#     "config": {
#         "data": {
#             "POSTGRES_DB": env["USER_DB_DB"],
#             "POSTGRES_USER": env["USER_DB_USER"],
#         }
#     },
#     "secrets": {
#         "data": {
#             "POSTGRES_PASSWORD": env["USER_DB_PASSWORD"],
#         }
#     },
# }


# if __name__ == "__main__":
#     # print(auth_config)
#     # print(celery_config)
#     # print(dms_config)
#     # print(registration_config)
#     # print(transaction_config)
#     # print(tx_db_config)
#     # print(user_db_config)

#     from auth.config import AuthConfig
#     config = dotenv_values("../backend/.env")
    
#     auth_config = AuthConfig(config)

#     print (auth_config.get_config_data())
    