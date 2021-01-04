#include <stdio.h>
#include <stdlib.h>
#include <string>
#include <iostream> 
#include <iomanip> 
#include <xgboost/c_api.h>
#include <argtable3.h>
#include "parse_parameters.h"
#include "config.h"

using namespace std;

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
        DMatrixHandle dtrain, dtest;
        safe_xgboost(XGDMatrixCreateFromFile(config.trainset.c_str(), config.silent, &dtrain));
        safe_xgboost(XGDMatrixCreateFromFile(config.evalset.c_str(), config.silent, &dtest));

        // create the booster
        BoosterHandle booster;
        DMatrixHandle eval_dmats[2] = {dtrain, dtest};
        safe_xgboost(XGBoosterCreate(eval_dmats, 2, &booster));

        // SET META PARAMETERS 
        // available parameters are described here:
        // https://xgboost.readthedocs.io/en/latest/parameter.html
        safe_xgboost(XGBoosterSetParam(booster, "tree_method",  "auto"));
        // avoid evaluating objective and metric on a GPU
        safe_xgboost(XGBoosterSetParam(booster, "gpu_id", "-1"));

        safe_xgboost(XGBoosterSetParam(booster, "objective", "reg:squarederror"));
        safe_xgboost(XGBoosterSetParam(booster, "min_child_weight", std::to_string(config.min_child_weight).c_str()));
        safe_xgboost(XGBoosterSetParam(booster, "gamma", std::to_string(config.gamma).c_str()));
        safe_xgboost(XGBoosterSetParam(booster, "max_depth", std::to_string(config.max_depth).c_str()));
        safe_xgboost(XGBoosterSetParam(booster, "lambda", std::to_string(config.lambda).c_str()));
        safe_xgboost(XGBoosterSetParam(booster, "alpha", std::to_string(config.alpha).c_str()));
        safe_xgboost(XGBoosterSetParam(booster, "max_delta_step", std::to_string(config.max_delta_step).c_str()));
        safe_xgboost(XGBoosterSetParam(booster, "eta", std::to_string(config.eta).c_str()));
        safe_xgboost(XGBoosterSetParam(booster, "nthread", std::to_string(config.nthreads).c_str()));
        safe_xgboost(XGBoosterSetParam(booster, "verbosity", std::to_string(config.silent).c_str()));

        // DO THE ACTUAL TRAINING
        int n_trees = config.n_trees;
        const char* eval_names[2] = {"train", "test"};
        const char* eval_result = NULL;
        for (int i = 0; i < n_trees; ++i) {
                safe_xgboost(XGBoosterUpdateOneIter(booster, i, dtrain));
                safe_xgboost(XGBoosterEvalOneIter(booster, i, eval_dmats, eval_names, 2, &eval_result));
                printf("%s\n", eval_result);
        }

        // PERFORM PREDICTION 
        if(config.perform_prediction) {
                bst_ulong out_len = 0;
                const float* out_result = NULL;
                const float* out_truelabel = NULL;

                int n_print = 0;
                XGDMatrixNumRow( dtest, &out_len);
                n_print = out_len;

                safe_xgboost(XGDMatrixGetFloatInfo(dtest, "label", &out_len, &out_truelabel));
                safe_xgboost(XGBoosterPredict(booster, dtest, 0, 0, 0, &out_len, &out_result));
                double mean_squared_error = 0;
                for (int i = 0; i < n_print; ++i) {
                        printf("pred: %1.4f \t true: %1.4f\n", out_result[i], out_truelabel[i]);
                        mean_squared_error += (out_result[i] - out_truelabel[i])*(out_result[i] - out_truelabel[i]);
                }
                mean_squared_error /= n_print;
                std::cout <<  setprecision(20) << std::fixed << "mean squared error " <<  mean_squared_error   << std::endl;
                printf("\n");
        }

        if(!config.output_modelfilename.empty()) { 
                XGBoosterSaveModel(booster, config.output_modelfilename.c_str());
        }

        // free everything
        safe_xgboost(XGBoosterFree(booster));
        safe_xgboost(XGDMatrixFree(dtrain));
        safe_xgboost(XGDMatrixFree(dtest));
        return 0;
}
