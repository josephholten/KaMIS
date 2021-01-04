#include <stdio.h>
#include <stdlib.h>

#include <iostream>
#include <string>
#include <xgboost/c_api.h>
#include <argtable3.h>
#include "parse_parameters.h"
#include "config.h"

#define safe_xgboost(call) {                                            \
        int err = (call);                                                       \
        if (err != 0) {                                                         \
                fprintf(stderr, "%s:%d: error in %s: %s\n", __FILE__, __LINE__, #call, XGBGetLastError()); \
                exit(1);                                                              \
        }                                                                       \
}

int main(int argc, char** argv) {
        Config config;
        int ret = parse_parameters(argc, argv, config);

        if(ret) exit(0);

        // load the data
        //
        //
        DMatrixHandle dtest;
        safe_xgboost(XGDMatrixCreateFromFile(config.evalset.c_str(), config.silent, &dtest));
        // set has to have a label column in order to make predictions, content is obsolte
        
        // create the booster
        BoosterHandle booster;
        XGBoosterCreate(NULL,0,&booster);
        XGBoosterSetParam(booster, "seed", "0");
        XGBoosterLoadModel(booster, config.input_modelname.c_str());
        safe_xgboost(XGBoosterSetParam(booster, "verbosity", std::to_string(config.silent).c_str()));

       
        // PERFORM PREDICTION 
        bst_ulong out_len = 0;
        const float* out_result = NULL;
        int n_print = 0;
        XGDMatrixNumRow( dtest, &out_len);
        n_print = out_len;

        safe_xgboost(XGBoosterPredict(booster, dtest, 0, 0, 0, &out_len, &out_result));
        for (int i = 0; i < n_print; ++i) {
                printf("%1.20f \n", out_result[i]);
        }
        
        // free everything
        safe_xgboost(XGBoosterFree(booster));
        safe_xgboost(XGDMatrixFree(dtest));
        return 0;
}
