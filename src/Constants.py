from src.AgentMode import AgentMode


class Constants:
    world_size = 250 / 1000  # 25 cm (250 mm)
    map_size = 1000
    update_time = 0.1  # (0.1 s)
    spawn_time = 1  # (1 s)
    refresh_time = 0.1  # (10 Hz)

    max_agents = 10

    agent_size = 2 / 1000  # (2 mm)
    norm_speed = 10 / 1000  # (10 mm/s)
    alarm_speed = 20 / 1000  # (20 mm/s)
    total_energy = 50  # (50 m)
    trail_energy = 10  # (10 m)
    trail_create_distance = agent_size * 2  # (2 x body length)
    recruit_create_distance = 0  # (continuous)

    pheromones = {
        'trail': {
            'decay_time': 48 / 5 * 60 * 60, # (48 hours in [s])
            'max_detect_range': 0,
            'action': 'attract',
        },
        'recruit': {
            'decay_time': 33 / 5 * 60,      # (33 mins in [s])
            'max_detect_range': 150 / 1e3,  # (15 cm in [m])
            'action': 'attract',
        },
        'repel': {
            'decay_time': 78 / 5 * 60,      # (78 min in [s])
            'max_detect_range': 300 / 1e3,  # (30 cm in [m])
            'action': 'repel',
        },
        'alarm': {
            'decay_time': 10 / 5 * 60,      # (10 min in [s])
            'max_detect_range': 300 / 1e3,  # (30 cm in [m])
            'action': 'alarm',
        },
    }
