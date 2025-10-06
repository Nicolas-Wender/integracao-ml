from src.factories.factory import Factory

# Instancia a factory e expõe o cliente já criado
api = Factory().create_client()

__all__ = ["api"]
