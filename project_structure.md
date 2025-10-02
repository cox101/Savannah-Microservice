savannah_microservice/
├── manage.py
├── requirements.txt
├── docker-compose.yml
├── Dockerfile
├── .env.example
├── .github/
│   └── workflows/
│       └── ci-cd.yml
├── helm/
│   └── savannah-microservice/
├── ansible/
│   └── playbook.yml
├── savannah_microservice/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── customers/
│   ├── __init__.py
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_models.py
│   │   ├── test_views.py
│   │   └── test_serializers.py
├── orders/
│   ├── __init__.py
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── tasks.py
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_models.py
│   │   ├── test_views.py
│   │   └── test_serializers.py
├── authentication/
│   ├── __init__.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── tests/
├── notifications/
│   ├── __init__.py
│   ├── sms.py
│   └── tests/
└── tests/
    ├── __init__.py
    └── conftest.py
