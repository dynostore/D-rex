#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>
#include <gsl/gsl_fit.h>
#include "prediction.h"
#include <gsl/gsl_multifit.h>

#define MAX_LINE_LENGTH 1024
#define MAX_FILE_NAME_LENGTH 256

// Function to fit a linear model and return the coefficients
int fit_linear_model(RealRecords *records, double *c0, double *c1, double *c2) {
    double x0[171];
    double x1[171];
    double y[171];
    
    for (int i = 0; i < 171; i++) {
        x0[i] = records->n[i];
        x1[i] = records->k[i];
        y[i] = records->avg_time[i];
    }

    gsl_multifit_linear_workspace *work = gsl_multifit_linear_alloc(171, 3);
    gsl_matrix *X = gsl_matrix_alloc(171, 3);
    gsl_vector *Y = gsl_vector_alloc(171);
    gsl_vector *c = gsl_vector_alloc(3);
    gsl_matrix *cov = gsl_matrix_alloc(3, 3);

    for (int i = 0; i < 171; i++) {
        gsl_matrix_set(X, i, 0, 1.0);
        gsl_matrix_set(X, i, 1, x0[i]);
        gsl_matrix_set(X, i, 2, x1[i]);
        gsl_vector_set(Y, i, y[i]);
    }

    double chisq;
    gsl_multifit_linear(X, Y, c, cov, &chisq, work);

    *c0 = gsl_vector_get(c, 0);
    *c1 = gsl_vector_get(c, 1);
    *c2 = gsl_vector_get(c, 2);

    gsl_multifit_linear_free(work);
    gsl_matrix_free(X);
    gsl_vector_free(Y);
    gsl_vector_free(c);
    gsl_matrix_free(cov);

    return 0; // Success
}

double predict(LinearModel models, double chunk_size, int min_bandwidth, int n, int k, double nearest_size, double file_size) {
    double transfer_time = calculate_transfer_time(chunk_size, min_bandwidth);
    
    printf("chunk size %f file size %f n %d k %d min bw %d\n", chunk_size, file_size, n, k, min_bandwidth);
    double Y_pred = models.intercept + models.slope_n * n + models.slope_k * k;
    Y_pred = Y_pred * (file_size / nearest_size);
    Y_pred /= 1000;  // Convert to seconds
    
    printf("Transfer time %f chunk time %f\n", transfer_time, Y_pred);
    return Y_pred + transfer_time;
}

double calculate_transfer_time(double chunk_size, double bandwidth) {
    return chunk_size / bandwidth;
}