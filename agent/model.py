import torch.nn as nn
import torch.nn.functional as F


class ActorCriticNetwork(nn.Module):
    def __init__(self, state_size, action_size):
        super(ActorCriticNetwork, self).__init__()
        self.shared_layers = nn.Sequential(
            nn.Linear(state_size, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU()
        )

        # Output cho xac suat cua cac hanh dong
        self.actor_head = nn.Linear(64, action_size)
        # Output cho gia tri trang thai
        self.critic_head = nn.Linear(64, 1)

    def forward(self, state):
        shared_features = self.shared_layers(state)
        action_probs = F.softmax(self.actor_head(shared_features), dim=-1)
        state_value = self.critic_head(shared_features)
        return action_probs, state_value
