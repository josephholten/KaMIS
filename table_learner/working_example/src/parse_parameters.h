/******************************************************************************
         * parse_parameters.h 
 * *
 * Source of KaHIP -- Karlsruhe High Quality Partitioning.
 * Christian Schulz <christian.schulz.phone@gmail.com>
 *****************************************************************************/


#ifndef PARSE_PARAMETERS_GPJMGSM8
#define PARSE_PARAMETERS_GPJMGSM8

#include <omp.h>
#include <string>
#include <sstream>
#include <argtable3.h>
#include "config.h"

int parse_parameters(int argn, char **argv, Config & config) {

        const char *progname = argv[0];

        // Setup argtable parameters.
        struct arg_lit *help                                 = arg_lit0(NULL, "help","Print help.");
        struct arg_lit *silent                               = arg_lit0(NULL, "silent","");
        struct arg_str *trainset                             = arg_strn(NULL, "trainset", NULL, 1, 1, "Path to csv train table.");
        struct arg_str *evalset                              = arg_strn(NULL, "evalset",  NULL, 1, 1, "Path to csv eval table.");
        struct arg_str *output_modelfilename                 = arg_str0(NULL, "output_filename",  NULL, "Output file name of model. If empty model will not be stored to disk.");
        struct arg_str *input_modelname                      = arg_strn(NULL, "input_modelname", NULL, 1, 1, "Path to file name of model. ");

        struct arg_int *n_trees                              = arg_int0(NULL, "n_trees", NULL, "Number of iterations.");
        
        struct arg_int *nthreads                             = arg_int0(NULL, "nthreads", NULL, "Number of threads to use.");
        struct arg_int *max_depth                            = arg_int0(NULL, "max_depth", NULL, "Number of threads to use.");

        struct arg_dbl *min_child_weight                     = arg_dbl0(NULL, "min_child_weight", NULL, "");
        struct arg_dbl *learning_rate                        = arg_dbl0(NULL, "learning_rate", NULL, "");
        struct arg_dbl *max_delta_step                       = arg_dbl0(NULL, "max_delta_step", NULL, "");
        struct arg_dbl *gamma                                = arg_dbl0(NULL, "gamma", NULL, "");
        struct arg_dbl *lambda                               = arg_dbl0(NULL, "lambda", NULL, "");
        struct arg_dbl *alpha                                = arg_dbl0(NULL, "alpha", NULL, "");

        struct arg_lit *perform_prediction                   = arg_lit0(NULL, "perform_prediction", "Perform prediction in the end and compare with evalset.");
        struct arg_end *end                                  = arg_end(100);
        
        // Define argtable.
        void* argtable[] = {
#ifdef PREDICT
                help, input_modelname, evalset, silent,
#else
                help, silent, trainset, evalset, n_trees, perform_prediction, nthreads, max_depth, min_child_weight, gamma, lambda, alpha, max_delta_step, learning_rate, output_modelfilename, 
#endif
                end
        };
        // Parse arguments.
        int nerrors = arg_parse(argn, argv, argtable);

        // Catch case that help was requested.
        if (help->count > 0) {
                printf("Usage: %s", progname);
                arg_print_syntax(stdout, argtable, "\n");
                arg_print_glossary(stdout, argtable,"  %-40s %s\n");
                arg_freetable(argtable, sizeof(argtable) / sizeof(argtable[0]));
                return 1;
        }


        if (nerrors > 0) {
                arg_print_errors(stderr, end, progname);
                printf("Try '%s --help' for more information.\n",progname);
                arg_freetable(argtable, sizeof(argtable) / sizeof(argtable[0]));
                return 1; 
        }

        if(trainset->count > 0) {
                config.trainset = trainset->sval[0];
        }

        if(evalset->count > 0) {
                config.evalset = evalset->sval[0];
        }

        if(n_trees->count > 0) {
                config.n_trees = n_trees->ival[0];
        } else {
                config.n_trees = 100;
        }

        if(nthreads->count > 0) {
                config.nthreads = nthreads->ival[0];
        } else {
                config.nthreads = 1;
        }

        if(perform_prediction->count > 0) {
                config.perform_prediction = true;
        } else {
                config.perform_prediction = false;
        }

        if(max_depth->count > 0) {
                config.max_depth = max_depth->ival[0];
        } else {
                config.max_depth = 6;
        }

        if(min_child_weight->count > 0) {
                config.min_child_weight = min_child_weight->dval[0];
        } else {
                config.min_child_weight = 1;
        }

        if(gamma->count > 0) {
                config.gamma = gamma->dval[0];
        } else {
                config.gamma = 0;
        }

        if(lambda->count > 0) {
                config.lambda = lambda->dval[0];
        } else {
                config.lambda = 1;
        }

        if(alpha->count > 0) {
                config.alpha = alpha->dval[0];
        } else {
                config.alpha = 0;
        }

        if(max_delta_step->count > 0) {
                config.max_delta_step = max_delta_step->dval[0];
        } else {
                config.max_delta_step = 0;
        }

        if(learning_rate->count > 0) {
                config.eta = learning_rate->dval[0];
        } else {
                config.eta = 0.3;
        }


        if(silent->count > 0) {
                config.silent = 1;
        } else {
                config.silent = 0;
        }

        if(output_modelfilename->count > 0) {
                config.output_modelfilename = output_modelfilename->sval[0];
        } 

        if(input_modelname->count > 0) {
                config.input_modelname = input_modelname->sval[0];
        } 



        return 0;
}

#endif /* end of include guard: PARSE_PARAMETERS_GPJMGSM8 */
