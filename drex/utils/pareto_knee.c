#include <stdio.h>
#include <math.h>
#include <float.h>
#include <stdlib.h>

// Function to calculate the bend angle for a 3D Pareto front
double calculate_bend_angle_3d(double x[3], double xL[3], double xR[3]) {
    // Extract objectives for each point
    double f1_x = x[0], f2_x = x[1], f3_x = x[2];
    double f1_xL = xL[0], f2_xL = xL[1], f3_xL = xL[2];
    double f1_xR = xR[0], f2_xR = xR[1], f3_xR = xR[2];
    
    // Calculate θL and θR for each plane (pair of objectives)
    double thetaL_f1_f2, thetaR_f1_f2;
    if (f1_x != f1_xL) {
        thetaL_f1_f2 = atan2(f2_xL - f2_x, f1_x - f1_xL);
    } else {
        thetaL_f1_f2 = (f2_xL > f2_x) ? M_PI / 2 : -M_PI / 2;
    }
    if (f1_xR != f1_x) {
        thetaR_f1_f2 = atan2(f2_x - f2_xR, f1_xR - f1_x);
    } else {
        thetaR_f1_f2 = (f2_x > f2_xR) ? M_PI / 2 : -M_PI / 2;
    }
    double bend_angle_f1_f2 = thetaL_f1_f2 - thetaR_f1_f2;
    
    double thetaL_f1_f3, thetaR_f1_f3;
    if (f1_x != f1_xL) {
        thetaL_f1_f3 = atan2(f3_xL - f3_x, f1_x - f1_xL);
    } else {
        thetaL_f1_f3 = (f3_xL > f3_x) ? M_PI / 2 : -M_PI / 2;
    }
    if (f1_xR != f1_x) {
        thetaR_f1_f3 = atan2(f3_x - f3_xR, f1_xR - f1_x);
    } else {
        thetaR_f1_f3 = (f3_x > f3_xR) ? M_PI / 2 : -M_PI / 2;
    }
    double bend_angle_f1_f3 = thetaL_f1_f3 - thetaR_f1_f3;
    
    double thetaL_f2_f3, thetaR_f2_f3;
    if (f2_x != f2_xL) {
        thetaL_f2_f3 = atan2(f3_xL - f3_x, f2_x - f2_xL);
    } else {
        thetaL_f2_f3 = (f3_xL > f3_x) ? M_PI / 2 : -M_PI / 2;
    }
    if (f2_xR != f2_x) {
        thetaR_f2_f3 = atan2(f3_x - f3_xR, f2_xR - f2_x);
    } else {
        thetaR_f2_f3 = (f3_x > f3_xR) ? M_PI / 2 : -M_PI / 2;
    }
    double bend_angle_f2_f3 = thetaL_f2_f3 - thetaR_f2_f3;
    
    // Average bend angle across all planes
    double bend_angle = (bend_angle_f1_f2 + bend_angle_f1_f3 + bend_angle_f2_f3) / 3;
    return bend_angle;
}

// Function to normalize the Pareto front values
void normalize_values(double pareto_front[][3], int num_points, double normalized_front[][3]) {
    double min_f1 = DBL_MAX, max_f1 = -DBL_MAX;
    double min_f2 = DBL_MAX, max_f2 = -DBL_MAX;
    double min_f3 = DBL_MAX, max_f3 = -DBL_MAX;

    // Find min and max values for each objective
    for (int i = 0; i < num_points; ++i) {
        if (pareto_front[i][0] < min_f1) min_f1 = pareto_front[i][0];
        if (pareto_front[i][0] > max_f1) max_f1 = pareto_front[i][0];
        if (pareto_front[i][1] < min_f2) min_f2 = pareto_front[i][1];
        if (pareto_front[i][1] > max_f2) max_f2 = pareto_front[i][1];
        if (pareto_front[i][2] < min_f3) min_f3 = pareto_front[i][2];
        if (pareto_front[i][2] > max_f3) max_f3 = pareto_front[i][2];
    }

    // Normalize the values
    for (int i = 0; i < num_points; ++i) {
        normalized_front[i][0] = (pareto_front[i][0] - min_f1) / (max_f1 - min_f1);
        normalized_front[i][1] = (pareto_front[i][1] - min_f2) / (max_f2 - min_f2);
        normalized_front[i][2] = (pareto_front[i][2] - min_f3) / (max_f3 - min_f3);
    }
}

// Function to find the knee point in a 3D Pareto front
int find_knee_point_3d(double pareto_front[][3], int num_points, double knee_point[3], int min_index, int max_index) {

    double normalized_front[num_points][3];
    normalize_values(pareto_front, num_points, normalized_front);
    int best_index;
    
    // Edge case handling: return value with smallest sum of normalized values
    if (num_points < 3) {
        //~ printf("Error: Need at least 3 points to compute the knee point. num_points=%d\n", num_points);
        double min_normalized_sum = DBL_MAX;
        double normalized_sum = DBL_MAX;
        for (int i = 0; i < num_points; i++) {
            normalized_sum = normalized_front[i][0] + normalized_front[i][1] + normalized_front[i][2];
            if (min_normalized_sum > normalized_sum) {
                min_normalized_sum = normalized_sum;
                best_index = i;
            }
        }
        return best_index;
    }
    
    double max_bend_angle = -DBL_MAX;
    double current_bend_angle;
    
    double xL[3] = { normalized_front[min_index][0], normalized_front[min_index][1], normalized_front[min_index][2] };
    double xR[3] = { normalized_front[max_index][0], normalized_front[max_index][1], normalized_front[max_index][2] };
    //~ printf("L %f %f %f R %f %f %f\n", pareto_front[min_index][0], pareto_front[min_index][1], pareto_front[min_index][2], pareto_front[max_index][0], pareto_front[max_index][1], pareto_front[max_index][2]);
    for (int i = 0; i < num_points; ++i) {
        double x[3] = { normalized_front[i][0], normalized_front[i][1], normalized_front[i][2] };
        
        current_bend_angle = calculate_bend_angle_3d(x, xL, xR);
        
        //~ printf("Point: (%.2f, %.2f, %.2f) Bend Angle: %.2f\n", x[0], x[1], x[2], current_bend_angle);
        
        if (current_bend_angle > max_bend_angle) {
            max_bend_angle = current_bend_angle;
            best_index = i;
            knee_point[0] = x[0];
            knee_point[1] = x[1];
            knee_point[2] = x[2];
        }
    }
    return best_index;
}

//~ int main() {
    //~ // Example Pareto front data (replace with your actual data)
    //~ double pareto_front[][3] = {
        //~ {1.0, 2.0, 3.0},
        //~ {2.0, 1.5, 2.5},
        //~ {1.5, 2.5, 1.5},
        //~ {1.2, 1.8, 2.2}
        //~ // Add more points here
    //~ };
    //~ int num_points = sizeof(pareto_front) / sizeof(pareto_front[0]);
        
    //~ double knee_point[3];
    //~ find_knee_point_3d(pareto_front, num_points, knee_point);
    
    //~ printf("Knee Point: (%.2f, %.2f, %.2f)\n", knee_point[0], knee_point[1], knee_point[2]);
    
    //~ return 0;
//~ }
