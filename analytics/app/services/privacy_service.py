def mask_account_number(account_number: str) -> str:
    parts = account_number.split("-", 1)
    if len(parts) != 2:
        return "****"
    prefix, suffix = parts
    visible = suffix[-4:] if len(suffix) >= 4 else suffix
    hidden = "*" * max(len(suffix) - len(visible), 4)
    return f"{prefix}-{hidden}{visible}"


def display_account_number(
    account_number: str,
    protected_accounts: set[str] | None = None,
) -> str:
    if protected_accounts and account_number in protected_accounts:
        return mask_account_number(account_number)
    return account_number
