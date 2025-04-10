#!/bin/bash

# Usage: wham [P|Ppi|Pval] hist_min hist_max num_bins tol temperature numpad #        metadatafile freefile [num_MC_trials randSeed]
./wham/wham/wham 0.1 1.2 100 0.0001 300.0 1 wham_metafile wham_freefile > wham_output 
