REGISTRY = {}

def register(name: str):
    def _wrap(cls):
        REGISTRY[name] = cls()
        return cls
    return _wrap

def get_adapter(name: str):
    try:
        return REGISTRY[name]
    except KeyError:
        raise KeyError(f"Adapter '{name}' no está registrado. Adapters disponibles: {list(REGISTRY.keys())}")
