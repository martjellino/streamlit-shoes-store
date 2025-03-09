class Shoes:
    def __init__(self, shoes_id, brand, model, category, color, size_eu, price_idr):
        self.shoes_id = shoes_id
        self.brand = brand
        self.model = model
        self.category = category
        self.color = color
        self.size_eu = size_eu
        self.price_idr = price_idr

    def able_to_kick_the_ball(self):
        return self.category == "Football"

    def able_to_run(self):
        running_categories = ["Running", "Basketball", "Football"]
        return self.category in running_categories


class Store:
    def __init__(self, store_id, store_name, store_address):
        self.store_id = store_id
        self.store_name = store_name
        self.store_address = store_address
        self.bunch_of_shoes = []
    
    def add_shoes_as_stock(self, shoes: Shoes):
        self.bunch_of_shoes.append(shoes)
        
    def get_shoes_suitable_for_football(self):
        return [shoe for shoe in self.bunch_of_shoes if shoe.able_to_kick_the_ball()]
    
    def get_shoes_suitable_for_running(self):
        return [shoe for shoe in self.bunch_of_shoes if shoe.able_to_run()]
        
