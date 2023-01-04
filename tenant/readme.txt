Commands to perform for launching tenants without any erros

1) Set default db for data
2) create 'log_db' for logging data
2) perform command: python3 manage.py makemigrations
3) perform command: python3 manage.py migrate tenant
4) Create tenants from python shell: python3 manage.py shell
    from tenant.models import Tenant
    tenant = Tenant.objects.create(name="tenant_name", schema_name="schema", sub_domain ="sub_domain_for_schema")
    tenant.save()
5) Perform default db migration : python3 manage.py migrate_schemas
6) Perfrom history table migration :  python3 manage.py migrate_history_schemas --database=log_db
7) create super users for schemas : python3 tenant_manage.py [schema_name] createsuperuser

                                all done enjoy !!!!!