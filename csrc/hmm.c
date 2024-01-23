#include <math.h>
#include <stdlib.h>
#include <stdio.h>

#include <hmm.h>

hmm_t* construct_hmm(unsigned long motion_num, double* init_prob, double** tr_prob, double** avrs, double** covars){
    hmm_t* hmm = (hmm_t*)malloc(sizeof(hmm_t));

    unsigned char n = motion_num;
    hmm->motion_num = n;

    hmm->init_prob = (double*)malloc(n * sizeof(double));
    hmm->tr_prob   = (double**)malloc(n * sizeof(double*));
    hmm->avrs      = (double**)malloc(n * sizeof(double*));
    hmm->covars    = (double**)malloc(n * sizeof(double*));

    for(unsigned char i = 0; i < n; ++i){
        hmm->init_prob[i] = init_prob[i];

        hmm->tr_prob[i] = (double*)malloc(n * sizeof(double));
        hmm->avrs[i]    = (double*)malloc(2 * sizeof(double));
        hmm->covars[i]  = (double*)malloc(3 * sizeof(double));

        for(unsigned char j = 0; j < n; ++j)
            hmm->tr_prob[i][j] = tr_prob[i][j];
        for(char d = 0; d < 2; ++d)
            hmm->avrs[i][d] = avrs[i][d];
        for(char d = 0; d < 3; ++d)
            hmm->covars[i][d] = covars[i][d];
    }

    return hmm;
}


void destroy_hmm(hmm_t* hmm){
    unsigned char n = hmm->motion_num;

    for(unsigned char i = 0; i < n; ++i){
        free(hmm->init_prob);
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


double baum_welch_once(hmm_t* hmm, unsigned int observation_len, double** observation){
    unsigned char n = hmm->motion_num;
    unsigned int size_n_dp = (unsigned int)n * (unsigned int)sizeof(double*);
    unsigned int size_n_d  = (unsigned int)n * (unsigned int)sizeof(double);

    unsigned int t_max = observation_len - 1;
    unsigned int size_ol_dp = observation_len * (unsigned int)sizeof(double*);
    unsigned int size_ol_d  = observation_len * (unsigned int)sizeof(double);

    double** b = (double**)malloc(size_n_dp); // gaussian cache
    for(unsigned char i = 0; i < n; ++i){
        b[i] = (double*)malloc(size_ol_d);
        for(unsigned int t = 0; t <= t_max; ++t){
            b[i][t] = gaussian(i, observation[t]);
        }
    }

    // ---------------------------------------------------
    // calculate forward probability & scaling coefficient
    // ---------------------------------------------------

    double** alpha = (double**)malloc(size_ol_dp); // forward prob
    double* c = (double*)malloc(size_ol_d);  // scaling coef
    c[0] = 1;

    //init
    alpha[0] = (double*)malloc(size_n_d);
    for(unsigned char i = 0; i < n; ++i)
        alpha[0][i] = n * b[i][0];

    // recurse
    for(unsigned int t = 1; t <= t_max; ++t){
        alpha[t] = (double*)malloc(size_n_d);
        for(unsigned char i = 0; i < n; ++i){
            alpha[t][i] = 0;
            for(unsigned char j = 0; j < n; ++j)
                alpha[t][i] += alpha[t - 1][j] * hmm->tr_prob[j][i] * b[i][t];
        }

        // calc c
        c[t] = 0;
        for(unsigned char i = 0; i < n; ++i)
            c[t] += alpha[t][i];

        // normalize
        // sum_i alpha_ti = 1
        for(unsigned char i = 0; i < n; ++i){
            alpha[t][i] /= c[t];
        }
    }


    // ------------------------------
    // calculate backward probability
    // ------------------------------

    double** beta = (double**)malloc(size_ol_dp); // backward prob

    // init
    beta[t_max] = (double*)malloc(size_n_d);
    for(unsigned char i = 0; i < n; ++i)
        beta[t_max][i] = 1;

    // recurse
    // * * * notion about t range * * *
    // type of t is unsigned
    // =>
    // t=0 --> --t --> underflow !
    // * * * * * * * * * * * * * * * * *
    for(unsigned int t = t_max - 1; t < t_max; --t){
        beta[t] = (double*)malloc(size_n_d);

        for(unsigned char i = 0; i < n; ++i){
            beta[t][i] = 0;
            for(unsigned char j = 0; j < n; ++j)
                beta[t][i] += hmm->tr_prob[i][j] * b[j][t] * beta[t + 1][j];
            beta[t][i] /= c[t];
        }
    }

    // ------------------------------------
    // calculate new transition probability
    // ------------------------------------

    double** new_tr_prob = (double**)malloc(size_n_dp);
    for(unsigned char i = 0; i < n; ++i){
        new_tr_prob[i] = (double*)malloc(size_n_d);
        float sum = 0;

        // calc new transition prob
        for(unsigned char j = 0; j < n; ++j){
            new_tr_prob[i][j] = 0;
            for(unsigned int t = 0; t <= t_max - 1; ++t){
                float temp = alpha[t][i] * hmm->tr_prob[i][j] * b[j][t + 1] * beta[t + 1][j];
                temp /= c[t];
                new_tr_prob[i][j] += temp;
            }
            sum += new_tr_prob[i][j];
        }

        // normalize
        // sum_j a_ij = 1
        for(unsigned char j = 0; j < n; ++j)
            new_tr_prob[i][j] /= sum;
    }

    // swap
    for(unsigned char i = 0; i < n; ++i){
        for(unsigned char j = 0; j < n; ++j){
            hmm->tr_prob[i][j] = new_tr_prob[i][j];
        }
        free(new_tr_prob[i]);
    }
    free(new_tr_prob);


    // --------------------------------
    // calculate logP(o; old parameter)
    // this is the return value
    // --------------------------------

    double liklihood = 0; // logP(o) , return value
    // ommit t=0 because c[t]=1
    for(unsigned int t = 1; t <= t_max; ++t){
        liklihood += logf(c[t]);
    }

    // delete no use array
    free(c);
    for(unsigned char i = 0; i < n; ++i)
        free(b[i]);
    free(b);

    // --------------------------------
    // calculate new Gaussian parameter
    // --------------------------------

    double** gamma = (double**)malloc(size_ol_dp); // P(s_t= i| o; old parameters)

    // gamma = alpha * beta
    for(unsigned int t = 0; t <= t_max; ++t){
        gamma[t] = (double*)malloc(size_n_d);
        float sum = 0;
        for(unsigned char i = 0; i < n; ++i){
            gamma[t][i] = alpha[t][i] * beta[t][i];
            sum += gamma[t][i];
        }

        // normalize
        // to reduce error
        for(unsigned char i = 0; i < n; ++i){
            gamma[t][i] /= sum;
        }
    }

    // delete no use array
    for(unsigned int t = 0; t <= t_max; ++t){
        free(alpha[t]);
        free(beta[t]);
    }
    free(alpha);
    free(beta);

    // calc
    for(unsigned char i = 0; i < n; ++i){
        float sum_gamma = 0; // sum_t gamma
        for(unsigned int t = 0; t <= t_max; ++t)
            sum_gamma += gamma[t][i];

        //calc new average of Gaussian
        double* new_avr = (double*)malloc(2 * sizeof(double)); // average
        for(unsigned char x = 0; x < 2; ++x){
            new_avr[x] = 0;
            for(unsigned int t = 0; t <= t_max; ++t)
                new_avr[x] += gamma[t][i] * observation[t][x];
            new_avr[x] /= sum_gamma;
        }

        // swap average
        for(unsigned char x = 0; x < 2; ++x)
            hmm->avrs[i][x] = new_avr[x];
        free(new_avr);

        // calc new covariance of Gaussian
        float new_cov_xx = 0; // covariance(x,x) (= var x)
        float new_cov_xy = 0; // covariance(x,y)
        float new_cov_yy = 0; // covariance(y,y) (= var y)
        // detが0になっちゃう-->次のループで破綻 要理論再確認
        for(unsigned int t = 0; t <= t_max; ++t){
            float x_ = observation[t][0] - hmm->avrs[i][0];
            float y_ = observation[t][1] - hmm->avrs[i][1];
            new_cov_xx += gamma[t][i] * x_ * x_;
            new_cov_xy += gamma[t][i] * x_ * y_;
            new_cov_yy += gamma[t][i] * y_ * y_;
        }
        new_cov_xx /= sum_gamma;
        new_cov_xy /= sum_gamma;
        new_cov_yy /= sum_gamma;

        // set covariance
        hmm->covars[i][0] = new_cov_xx;
        hmm->covars[i][1] = new_cov_xy;
        hmm->covars[i][2] = new_cov_yy;
    }

    // ----------------------------------------
    // calculate new initial motion probability
    // ----------------------------------------

    for(unsigned char i = 0; i < n; ++i)
        hmm->init_prob[i] = gamma[0][i];

    // delete gamma
    for(unsigned int t = 0; t <= t_max; ++t)
        free(gamma[t]);
    free(gamma);


    return liklihood;

}


void baum_welch(hmm_t* hmm, unsigned int observation_len, double** observation){
    return;

    double likilihood; // logP(o)
    double diff_liklihood_threshold = 0.001;
    int update_loop_max = 2;

    // init
    likilihood = update_once(observation_len, observation);

    // loop update untill logP(o) converge
    int update_cnt = 1;
    for(; update_cnt < update_loop_max; ++update_cnt){
        float new_likilihood = update_once(observation_len, observation);
        if(new_likilihood - likilihood <= diff_liklihood_threshold)
            break;
        likilihood = new_likilihood;
    }
    // ***** note ***********************************************************
    //
    // logP(o) gets larger at every update according to Baum-Welch algorhytm.
    // =>
    // once logP(o; new) - logP(o; old) is enogh small, logP(o) is converged.
    //
    // **********************************************************************

    return;
}
