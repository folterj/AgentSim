class Constants:
    world_size = 250.0 / 1000  # 25 cm (250 mm)
    update_time = 0.1  # (0.1 s)
    slow_update_interval = 10
    spawn_time = 1  # (1 s)
    refresh_time = 0.1  # (10 Hz)

    max_agents = 10

    agent_size = 2.0 / 1000  # (2 mm)
    norm_speed = 10.0 / 1000  # (10 mm/s)
    alarm_speed = 20.0 / 1000  # (20 mm/s)
    total_energy = 50  # (50 m)
    trail_energy = 10  # (10 m)
    trail_create_distance = agent_size * 2  # (2 x body length)
    recruit_create_distance = 0  # (continuous)
