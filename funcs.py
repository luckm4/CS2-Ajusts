def world_to_screen(pos, matrix, window_size):
    sight_x = window_size[0] / 2
    sight_y = window_size[1] / 2

    # Transformação 3D para coordenadas de clip
    clip_coords_x = pos[0] * matrix[0][0] + pos[1] * matrix[0][1] + pos[2] * matrix[0][2] + matrix[0][3]
    clip_coords_y = pos[0] * matrix[1][0] + pos[1] * matrix[1][1] + pos[2] * matrix[1][2] + matrix[1][3]
    clip_coords_z = pos[0] * matrix[2][0] + pos[1] * matrix[2][1] + pos[2] * matrix[2][2] + matrix[2][3]
    clip_coords_w = pos[0] * matrix[3][0] + pos[1] * matrix[3][1] + pos[2] * matrix[3][2] + matrix[3][3]

    # Se a coordenada w for muito pequena, significa que o objeto está fora da visão
    if clip_coords_w < 0.1:
        return False

    # Transformando as coordenadas de clip para NDC (Normalized Device Coordinates)
    ndc_x = clip_coords_x / clip_coords_w
    ndc_y = clip_coords_y / clip_coords_w

    # Convertendo para coordenadas de tela
    screen_x = (sight_x * ndc_x) + sight_x
    screen_y = -(sight_y * ndc_y) + sight_y

    return (screen_x, screen_y)