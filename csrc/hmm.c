#include <math.h>
#include <stdlib.h>
#include <stdio.h>

#include <hmm.h>

hmm_t* construct_hmm(unsigned long motion_num, double* tr_prob, double* avrs, double* covars){
    hmm_t* hmm = (hmm_t*)malloc(sizeof(hmm_t));

    unsigned long n = motion_num;
    hmm->motion_num = n;

    hmm->tr_prob = (double**)malloc(n * sizeof(double*));
    hmm->avrs    = (double**)malloc(n * sizeof(double*));
    hmm->covars  = (double**)malloc(n * sizeof(double*));

    for(unsigned long i = 0; i < n; ++i){
        hmm->tr_prob[i] = (double*)malloc(n * sizeof(double));
        hmm->avrs[i]    = (double*)malloc(2 * sizeof(double));
        hmm->covars[i]  = (double*)malloc(3 * sizeof(double));

        for(unsigned long j = 0; j < n; ++j)
            hmm->tr_prob[i][j] = tr_prob[i*n + j];
        for(char d = 0; d < 2; ++d)
            hmm->avrs[i][d] = avrs[i*2+d];
        for(char d = 0; d < 3; ++d)
            hmm->covars[i][d] = covars[i*3+d];
    }

    return hmm;
}


void destroy_hmm(hmm_t* hmm){
    unsigned long n = hmm->motion_num;

    for(unsigned long i = 0; i < n; ++i){
        free(hmm->tr_prob[i]);
        free(hmm->avrs[i]);
        free(hmm->covars[i]);
    }

    free(hmm->tr_prob);
    free(hmm->avrs);
    free(hmm->covars);

    free(hmm);

    return;
}


void baum_welch(hmm_t* hmm, double** observation){
    return;
}
