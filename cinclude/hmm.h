#ifndef __WILI_HMM_H__
#define __WILI_HMM_H__

typedef struct{
    unsigned char motion_num;
    double* init_prob;
    double** tr_prob;
    double** avrs;
    double** covars;
} hmm_t;

hmm_t* construct_hmm(unsigned long motion_num, double* init_prob, double** tr_prob, double** avrs, double** covars);
void destroy_hmm(hmm_t* hmm_ptr);

void baum_welch(hmm_t* param_ptr, unsigned int observation_len, double** observation);

#endif