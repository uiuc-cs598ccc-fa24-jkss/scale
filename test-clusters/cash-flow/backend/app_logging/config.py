import logging.config

logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'default'
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'app.log',
            'formatter': 'default'
        }
    },
    'loggers': {
        'AuthService': {
            'level': 'DEBUG',
            'handlers': ['console', 'file']
        },

        'TransactionService': {
            'level': 'DEBUG',
            'handlers': ['console', 'file']
        },
        
        'TaskingService': {
            'level': 'DEBUG',
            'handlers': ['console', 'file']
        },
        
        'DataService': {
            'level': 'DEBUG',
            'handlers': ['console', 'file']
        },                

        'RegistrationService': {
            'level': 'DEBUG',
            'handlers': ['console', 'file']
        },    

        'NotificationService': {
            'level': 'DEBUG',
            'handlers': ['console', 'file']
        },    
   
    }
})
