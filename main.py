import numpy as np
import torch
from environment.eon_env import EONEnvironment
from environment.topology import create_nsfnet_topology, create_random_erdos_renyi_topology
from environment.traffic_generator import RandomTrafficGenerator
from agent.drl_agent import DRLAgent
from utils.config import config
from utils.plotting import plot_learning_curve, plot_blocking_rate_comparison
from utils.logger import setup_logging


def train_drl_agent(env, agent, num_episodes, max_steps_per_episode, update_frequency, logger):
    logger.info("Starting DRL agent training ...")
    rewards_history = []
    for episode in range(num_episodes):
        state = env.reset()
        episode_rewards = []
        log_probs = []
        values = []
        next_values = []
        dones = []
        for step in range(max_steps_per_episode):
            request = env.get_next_service_request()
            if not request:
                break

            action, prob, value = agent.select_action(state)
            next_state, reward, done, info = env.step(action)

            episode_rewards.append(reward)
            log_probs.append(prob[0, action].unsqueeze(0))
            values.append(value)

            next_values.append(agent.actor_critic(
                torch.FloatTensor(next_state).unsqueeze(0))[1])

            state = next_state
            if done:
                break

        avg_reward = np.mean(episode_rewards)
        rewards_history.append(avg_reward)
        logger.info(
            f"Episode {episode+1}/{num_episodes}, Average Reward: {avg_reward:.4f}")

        if (episode + 1) % update_frequency == 0:
            actor_loss, critic_loss, total_loss = agent.update_model(
                episode_rewards, log_probs, values, next_values, dones)
            logger.info(
                f" Model update - Actor Loss: {actor_loss:.4f}, Critic Loss: {critic_loss:.4f}, Total Loss: {total_loss:.4f}")

    plot_learning_curve(rewards_history, "ActorCriticNetwork",
                        filepath=config.results_dir + "ActorCriticNetwork_learning_curve.png")
    agent.save_model(config.model_save_path)
    return agent


def evaluate_algorithms(env, drl_agent, num_episodes, logger):
    logger.info("Starting evaluation ...")
    algorithm_names = ["ActorCriticNetwork"]
    blocking_rates = []

    logger.info("Evaluating ActorCriticNetwork ...")
    drl_agent.load_model(config.model_save_path)
    drl_agent.actor_critic.eval()
    blocked_request_drl = 0
    for episode in range(num_episodes):
        state = env.reset()
        for step in range(config.max_steps_per_episode):
            request = env.get_next_service_request()
            if not request:
                break

            action, _, _ = drl_agent.select_action(state)
            _, reward, done, info = env.step(action)
            if info['action_taken'] == 'block':
                blocked_request_drl += 1
            if done:
                break

    blocking_rate_drl = blocked_request_drl / \
        (num_episodes * config.max_steps_per_episode)

    blocking_rates.append(blocking_rate_drl)
    logger.info(f"DRL agent blocking rate: {blocking_rate_drl:.4f}")

    plot_blocking_rate_comparison(blocking_rates, algorithm_names,
                                  filepath=config.results_dir + "blocking_rate_comparison.png")
    logger.info("Algorithm evaluation finished, blocking rates plot is saved")


def main():
    logger = setup_logging()
    logger.info("Starting simulation")

    topology_data = create_random_erdos_renyi_topology()
    traffic_generator = RandomTrafficGenerator(
        config.arrival_rate, config.duration_mean)
    env = EONEnvironment(
        topology_data, config.num_wavelengths, traffic_generator)

    state_size = len(env._get_state())
    action_size = config.num_wavelengths + 1
    drl_agent = DRLAgent(state_size, action_size,
                         learning_rate=config.learning_rate, gamma=config.gamma)

    trained_agent = train_drl_agent(
        env=env, agent=drl_agent, num_episodes=config.num_episodes, max_steps_per_episode=config.max_steps_per_episode, update_frequency=config.update_frequency, logger=logger)
    evaluate_algorithms(env=env, drl_agent=trained_agent,
                        num_episodes=config.evaluation_episodes, logger=logger)

    logger.info("Simulation is completed")


if __name__ == "__main__":
    main()
