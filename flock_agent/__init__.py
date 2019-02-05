from .flock_agent import FlockAgent

flock_agent_version = 0.1


def main():
    agent = FlockAgent(flock_agent_version)
    agent.status()
