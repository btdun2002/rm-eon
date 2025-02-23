import torch
import torch.distributions
import numpy as np
import torch.optim as optim
from agent.model import ActorCriticNetwork


class DRLAgent:
    def __init__(self, state_size, action_size, learning_rate=1e-3, gamma=0.99):
        self.actor_critic = ActorCriticNetwork(state_size, action_size)
        self.optimizer = optim.Adam(
            self.actor_critic.parameters(), lr=learning_rate)
        self.gamma = gamma

    def select_action(self, state):
        # Chuyen doi dinh dang input
        state = torch.FloatTensor(state).unsqueeze(0)
        probs, value = self.actor_critic(state)
        # Tra ve object cho phan bo xac suat cua cac hanh dong
        action_prob = torch.distributions.Categorical(probs)
        # Tra ve action ngau nhien, dua tren phan bo xac suat cua cac hanh dong
        action = action_prob.sample()
        return action.item(), probs, value

    def update_model(self, rewards, log_probs, values, next_values, dones):
        """
        log_probs (list): Danh sach gia tri logarit cua xac suat moi action tai mot step
        dones (list): Xac dinh episode da hoan thanh tai step day chua
        """
        rewards = torch.FloatTensor(rewards)
        values = torch.FloatTensor(values)
        log_probs = torch.stack(log_probs)
        next_values = torch.FloatTensor(next_values)
        dones = torch.FloatTensor(dones)

        advantages = rewards + self.gamma * next_values * (1 - dones) - values
        actor_loss = (-log_probs * advantages.detach()).mean()
        critic_loss = advantages.pow(2).mean()
        total_loss = actor_loss + critic_loss

        self.optimizer.zero_grad()
        total_loss.backward()
        # Thuc hien cap nhat tham so cua mo hinh
        self.optimizer.step()
        return actor_loss.item(), critic_loss.item(), total_loss.item()

    def save_model(self, filepath):
        torch.save(self.actor_critic.state_dict(), filepath)

    def load_model(self, filepath):
        self.actor_critic.load_state_dict(torch.load(filepath))


if __name__ == '__main__':
    test_state_size = 140
    test_action_size = 11

    agent = DRLAgent(test_state_size, test_action_size)
    dummy_state = np.random.rand(test_state_size)
    test_action, test_probs, test_value = agent.select_action(dummy_state)
    print("Selected Action:", test_action)
    print("Action Probabilities", test_probs)
    print("Value:", test_value)
