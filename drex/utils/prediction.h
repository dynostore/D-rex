#ifndef PREDICT_H
#define PREDICT_H

typedef struct {
    double *n;
    double *k;
    double *avg_time;
    int size;
} RealRecords;

typedef struct {
    double intercept;
    double slope_n;
    double slope_k;
} LinearModel;

RealRecords* read_real_records(const char *dir_data, int *num_sizes);
//~ LinearModel* fit_linear_model(RealRecords *records, int num_files);
int fit_linear_model(RealRecords *records, double *c0, double *c1, double *c2);
double predict(LinearModel models, double chunk_size, int min_bandwidth, int n, int k, double nearest_size, double file_size);
double calculate_transfer_time(double chunk_size, double bandwidth);

#endif
