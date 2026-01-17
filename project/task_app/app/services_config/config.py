from fastapi.security import OAuth2PasswordBearer
KEYCLOAK_SERVER_URL = "http://localhost:8080/"
KEYCLOAK_REALM = "{test_realm}"
KEYCLOAK_CLIENT_ID = "{test_fastapi_client}"
KEYCLOAK_CLIENT_SECRET = "{test_client_secret}"
CERTS_URL = f"{KEYCLOAK_SERVER_URL}realms/{KEYCLOAK_REALM}/protocol/openid-connect/certs"
GRANT_TYPE ="password"
TOKEN_URL = f"{KEYCLOAK_SERVER_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/token"
USERNAME = "Test_user"
PASSWORD = "test_pass"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{KEYCLOAK_SERVER_URL}realms/{KEYCLOAK_REALM}/protocol/openid-connect/token")

MAIL_SUBJECT = "New Task Created | Review and Take Action"
MAIL_BODY = (
    "Hello,\n\n"
    "This is to inform you that a new task has been successfully created in the system.\n"
    "Kindly review the task details, verify the assigned responsibilities, and proceed with the required actions.\n"
    "Please ensure timely completion as per the defined priority and deadlines.\n\n"
    "Regards,\n"
    "Task Management System"
)
TO_ADDRESS = '{reciever_mail}'
GMAIL_USER = "{sender_mail}"
GMAIL_APP_PASSWORD = "{smtp_key}"
REDIS_URL = "redis://localhost:6379/0"
DATABASE_URL = "{test_databse_url}"