from django.utils.translation import ugettext_lazy as _
from rest_framework import HTTP_HEADER_ENCODING, authentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed, InvalidToken, TokenError
from rest_framework_simplejwt.models import TokenUser
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.state import User
# tenant aware
# from django_tenants.middleware.main import TenantMainMiddleware
from tenant.utils import hostname_from_request
AUTH_HEADER_TYPES = api_settings.AUTH_HEADER_TYPES

if not isinstance(api_settings.AUTH_HEADER_TYPES, (list, tuple)):
    AUTH_HEADER_TYPES = (AUTH_HEADER_TYPES,)

AUTH_HEADER_TYPE_BYTES = set(
    h.encode(HTTP_HEADER_ENCODING)
    for h in AUTH_HEADER_TYPES
)


class JWTAuthentication(authentication.BaseAuthentication):
    """
    An authentication plugin that authenticates requests through a JSON web
    token provided in a request header.
    """
    www_authenticate_realm = 'api'

    def authenticate(self, request):
        header = self.get_header(request)
        if header is None:
            return None

        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)

        return self.get_user(validated_token, request), validated_token

    def authenticate_header(self, request):
        return '{0} realm="{1}"'.format(
            AUTH_HEADER_TYPES[0],
            self.www_authenticate_realm,
        )

    def get_header(self, request):
        """
        Extracts the header containing the JSON web token from the given
        request.
        """
        header = request.META.get('HTTP_AUTHORIZATION')

        if isinstance(header, str):
            # Work around django test client oddness
            header = header.encode(HTTP_HEADER_ENCODING)

        return header

    def get_raw_token(self, header):
        """
        Extracts an unvalidated JSON web token from the given "Authorization"
        header value.
        """
        parts = header.split()

        if len(parts) == 0:
            # Empty AUTHORIZATION header sent
            return None

        if parts[0] not in AUTH_HEADER_TYPE_BYTES:
            # Assume the header does not contain a JSON web token
            return None

        if len(parts) != 2:
            raise AuthenticationFailed(
                _('Authorization header must contain two space-delimited values'),
                code='bad_authorization_header',
            )

        return parts[1]

    def get_validated_token(self, raw_token):
        """
        Validates an encoded JSON web token and returns a validated token
        wrapper object.
        """
        messages = []
        for AuthToken in api_settings.AUTH_TOKEN_CLASSES:
            try:
                return AuthToken(raw_token)
            except TokenError as e:
                messages.append({'token_class': AuthToken.__name__,
                                 'token_type': AuthToken.token_type,
                                 'message': e.args[0]})

        raise InvalidToken({
            'detail': _('Given token not valid for any token type'),
            'messages': messages,
        })

    def get_user(self, validated_token, request):
        domain_from_request = hostname_from_request(request)

        """
        Attempts to find and return a user using the given validated token.
        """
        # get domain_name from the request

        try:
            user_id = validated_token[api_settings.USER_ID_CLAIM]
            # to validate users from multiple tenants
            user_name = validated_token['user_name']
            domain_name = validated_token['domain_name']
        except KeyError:
            raise InvalidToken(_('Token contained no recognizable user identification'))

        if domain_from_request != domain_name:
            raise InvalidToken(_('The host name of token does not match, please try valid host name'))

        try:
            user = User.objects.get(**{api_settings.USER_ID_FIELD: user_id}, user_name=user_name)
            # user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise AuthenticationFailed(_('User not found'), code='user_not_found')

        if not user.is_active:
            raise AuthenticationFailed(_('User is inactive'), code='user_inactive')

        return user


class JWTTokenUserAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        """
        Returns a stateless user object which is backed by the given validated
        token.
        """
        if api_settings.USER_ID_CLAIM not in validated_token:
            # The TokenUser class assumes tokens will have a recognizable user
            # identifier claim.
            raise InvalidToken(_(
                'Token contained no recognizable user identification, should contain user_id, user_name, domain_name'))

        return TokenUser(validated_token)
