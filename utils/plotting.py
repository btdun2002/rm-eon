import matplotlib.pyplot as plt


def plot_learning_curve(rewards_history, algorithm_name, filepath="results/learning_curve.png"):
    plt.figure(figsize=(10, 6))
    plt.plot(rewards_history)
    plt.xlabel("Episodes")
    plt.ylabel("Average Reward")
    plt.title(f"Learning Curve - {algorithm_name}")
    plt.grid(True)
    plt.savefig(filepath)
    plt.close()


def plot_blocking_rate_comparison(blocking_rates, algorithm_names, filepath="results/blocking_rate_comparison.png"):
    plt.figure(figsize=(10, 6))
    plt.bar(algorithm_names, blocking_rates)
    plt.ylabel("Blocking Probability")
    plt.title("Blocking Rate Comparison")
    plt.savefig(filepath)
    plt.close()
