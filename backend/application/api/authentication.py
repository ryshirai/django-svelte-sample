from rest_framework.authentication import SessionAuthentication
from rest_framework.request import Request


class SessionCsrfAuthentication(SessionAuthentication):
    # 未ログインの POST でも CSRF を見る。DRF 既定は認証済みだけ。
    def authenticate(self, request: Request) -> tuple[object, None] | None:
        user = getattr(request._request, "user", None)
        self.enforce_csrf(request)
        if not user or not user.is_active:
            return None
        return (user, None)
