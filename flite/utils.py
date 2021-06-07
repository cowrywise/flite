import secrets


def unique_reference(model, filters={}, len=12):
    ref = secrets.token_hex(len)
    while model.objects.filter(reference=ref, **filters).exists():
        ref = secrets.token_hex(len)
    return ref
