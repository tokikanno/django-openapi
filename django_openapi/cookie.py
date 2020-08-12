from django import VERSION as DJANGO_VERSION

_SUPPORT_SAMESITE_COOKIE = (DJANGO_VERSION[0], DJANGO_VERSION[1]) >= (2, 1)


class CookieJar(object):
    def __init__(self):
        self.cookie_operations = []

    def _check_samesite_support(self, samesite):
        if samesite is not None and not _SUPPORT_SAMESITE_COOKIE:
            raise ValueError('samesite cookie is not support in your django version')

    def set_cookie(
        self,
        key,
        value='',
        max_age=None,
        expires=None,
        path='/',
        domain=None,
        secure=False,
        httponly=False,
        samesite=None,
    ):
        self._check_samesite_support(samesite)
        arg_d = dict(
            key=key,
            value=value,
            max_age=max_age,
            expires=expires,
            path=path,
            domain=domain,
            secure=secure,
            httponly=httponly,
        )
        if _SUPPORT_SAMESITE_COOKIE:
            arg_d['samesite'] = samesite

        self.cookie_operations.append(('set_cookie', arg_d))

    def delete_cookie(self, key, path='/', domain=None, samesite=None):
        self._check_samesite_support(samesite)
        arg_d = dict(key=key, path=path, domain=domain,)
        if _SUPPORT_SAMESITE_COOKIE:
            arg_d['samesite'] = samesite

        self.cookie_operations.append(('delete_cookie', arg_d))

    def apply_to_response(self, response):
        op_type_to_fn_map = {}

        for op_type, arg_d in self.cookie_operations:
            if op_type not in op_type_to_fn_map:
                op_type_to_fn_map[op_type] = getattr(response, op_type)

            fn = op_type_to_fn_map[op_type]
            fn(**arg_d)
