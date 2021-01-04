
#ifndef CONFIG_DI1ES4T0
#define CONFIG_DI1ES4T0

#include <iosfwd>
#include <string> 

using namespace std;

struct Config
{
        Config() {}

        string trainset;
        string evalset;
        string output_modelfilename;
        string input_modelname;

        int n_trees;
        bool perform_prediction;

        
        int nthreads;
        
        bool silent; 

        //model parameters
        double gamma;
        int max_depth;
        double lambda; 
        double alpha;
        double min_child_weight;
        double max_delta_step;
        double eta;

};


#endif 
