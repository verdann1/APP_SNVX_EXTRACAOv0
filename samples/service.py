from samples.repository import SampleRepository

class SampleService:
    def __init__(self):
        self.sample_repository = SampleRepository()

    def get_samples(self):
        """Obtém amostras via repositório"""
        return self.sample_repository.get_samples()

    def get_sample_stats(self):
        """Obtém estatísticas das amostras"""
        return self.sample_repository.get_sample_stats()

    def create_sample(self, assembly_id, product_id):
        """
        Cria uma nova amostra com um único produto
        
        Args:
            assembly_id (int): ID da montagem associada
            product_id (int): ID do produto único associado
        """
        if not isinstance(product_id, int):
            raise ValueError("product_id deve ser um inteiro válido")
            
        sample_data = {
            'assembly': assembly_id,
            'products': [product_id]  # Garante formato de lista para compatibilidade
        }
        return self.sample_repository.create_sample(sample_data)