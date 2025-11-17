import numpy as np

global_normal = np.array([1.0, 0, 0])
beam_direction = np.array([10.0, 3.0, 0])
beam_direction /= np.linalg.norm(beam_direction)
focal_length = 10

offset_vector = np.array([0, 1.0, 0])
offset_vector /= np.linalg.norm(offset_vector)
input_slope = np.dot(beam_direction, offset_vector) / np.dot(
    beam_direction, global_normal
)
output_slope = input_slope - np.linalg.norm(offset_vector) / focal_length

input_angle = np.arctan(input_slope)
output_angle = np.arctan(output_slope)
rotation_axis = np.cross(offset_vector, global_normal)
rotation_axis /= np.linalg.norm(rotation_axis)

angle_offset = output_angle - input_angle
print("Angle Offset (degrees):", np.degrees(angle_offset))
