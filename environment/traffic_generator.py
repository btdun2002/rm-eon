import random


class RandomTrafficGenerator:
    """
    arrival_rate (float): Toc do den trung binh cua cac yeu cau dich vu (Poisson)
    duration_mean (float): Thoi luong trung binh cua cac yeu cau dich vu (Cap so nhan)
    demand (int): Luong bang thong yeu cau cho moi dich vu
    """

    def __init__(self, arrival_rate, duration_mean):
        self.arrival_rate = arrival_rate
        self.duration_mean = duration_mean
        self.service_id_counter = 0

    def generate_request(self, nodes):
        if random.random() < self.arrival_rate:
            self.service_id_counter += 1
            source, destination = random.sample(nodes, 2)
            demand = random.randint(10, 100)
            duration = random.expovariate(1.0 / self.duration_mean)
            print("Request is generated")
            return {
                'service_id': self.service_id_counter,
                'source': source,
                'destination': destination,
                'demand': demand,
                'duration': duration
            }
        print("Request is not generated")
        return None
