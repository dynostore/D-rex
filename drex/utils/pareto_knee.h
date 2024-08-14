#ifndef PARETO_H
#define PARETO_H

double calculate_bend_angle_3d(double x[3], double xL[3], double xR[3]);
void normalize_values(double pareto_front[][3], int num_points, double normalized_front[][3]);
int find_knee_point_3d(double pareto_front[][3], int num_points, double knee_point[3], int min_index, int max_index);

#endif
