import utils.logger as logger
import entity as ett


class resourceManager():
    def __init__(self):
        self.logger = logger.Ranker_Logger().get_logger()
        self.entity_list = []

    def get_entity_list(self):
        return self.entity_list
    
    def add_entity(self, entity):
        self.entity_list.append(entity)

    def update_entity(self, entity):
        for index, item in enumerate(self.entity_list):
            if item.model == entity.model:
                self.entity_list[index] = entity
                return True
        return False
    

class fakeResourceManager(resourceManager):
    def __init__(self):
        super().__init__()
        self.logger.info('Fake resource manager created.')
        
    def add_entity(self, entity):
        self.logger.info('Fake resource added.')
        super().add_entity(entity)
        
    def update_entity(self, entity):
        self.logger.info('Fake resource updated.')
        super().update_entity(entity)
        
    def get_entity_list(self):
        self.logger.info('Fake resource list returned.')
        return super().get_entity_list()
        
    def get_json(self):
        self.logger.info('Fake resource list returned in JSON format.')
        return ett.CombatResourceList(self.entity_list).get_json()