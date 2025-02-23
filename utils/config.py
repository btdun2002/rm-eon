class Config:
    def __init__(self):
        self.topology_type = "NSFNET"
        self.num_wavelengths = 10

        self.arrival_rate = 0.5
        self.duration_mean = 5

        self.learning_rate = 1e-3
        self.gamma = 0.99
        self.batch_size = 64
        self.num_episodes = 1000
        self.max_steps_per_episode = 200
        self.update_frequency = 4

        self.evaluation_episodes = 100

        self.results_dir = "results/"
        self.model_save_path = "results/drl_agent_model.d"


config = Config()
