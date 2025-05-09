class Constants:
    map_filename = 'maps/simple_maze.png'
    world_size = 2.5  # 250 cm (2.5 m)
    update_time = 1  # (1 s)
    spawn_time = 1  # (1 s)
    refresh_time = 0.1  # (10 Hz)

    max_agents = 10

    agent_size = 2e-3  # (2 mm)
    hive_size = 2e-3
    food_size = 2e-3
    pheromone_size = 2e-4  # (0.2 mm)
    norm_speed = 10e-3  # (10 mm/s)
    alarm_speed = 20e-3  # (20 mm/s)
    total_energy = 50  # (50 m)
    trail_energy = 10  # (10 m)

    pheromones = {
        'alarm': {
            'decay_time': 10 / 5 * 60,      # (10 min in [s])
            'max_detect_range': 300 / 1e3,  # (30 cm in [m])
            'action': 'alarm',
        },
        'repel': {
            'decay_time': 78 / 5 * 60,      # (78 min in [s])
            'max_detect_range': 300 / 1e3,  # (30 cm in [m])
            'action': 'repel',
        },
        'recruit': {
            'decay_time': 33 / 5 * 60,      # (33 mins in [s])
            'max_detect_range': 150 / 1e3,  # (15 cm in [m])
            'action': 'attract',
        },
        'trail': {
            'decay_time': 48 / 5 * 60 * 60,  # (48 hours in [s])
            'max_detect_range': agent_size,
            'action': 'attract',
        },
    }
