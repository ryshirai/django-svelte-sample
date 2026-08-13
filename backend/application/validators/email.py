def normalize_email(*, email: str) -> str:
    # 前後空白除去と小文字化。username と email の両方にこれを入れる。
    return email.strip().lower()
