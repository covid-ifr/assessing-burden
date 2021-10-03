data {
  int num_loc_ifr; // number of locations with fatality data
  int num_loc_all; // total number of locations (with or without fatality data)
  int length_dstar; 
  int length_rstar;
  
  int study_match_pi[length_rstar]; // match test kit to pi_A
  
  int D_star[length_dstar]; // # deaths each age bin loc1, # deaths loc2, ...
  vector[length_dstar] N; // population each age bin/loc matching D_star
  int R_star[length_rstar]; // # tested positive each age bin loc1, loc2, ...
  int n[length_rstar]; // # tested each age bin loc1, loc2, ...
  
  int num_test;
  int<lower=0> sens_n[num_test]; // number of positive controls tested
  int<lower=0> sens_x[num_test]; // number of positive controls that tested positive
  int<lower=0> spec_n[num_test]; // number of negative controls tested
  int<lower=0> spec_x[num_test]; // number of negative controls that tested negative
  
  int min_match_sero_to_death[length_dstar]; // smallest R_star index that overlaps 
                                             // corresponding D_star bin
  int max_match_sero_to_death[length_dstar]; // largest R_star index that overlaps 
                                             // corresponding D_star bin
  int min_match_total_sero[num_loc_all]; // smallest serology age bin in corresponding 
                                         // location
  int max_match_total_sero[num_loc_all]; // largest serology age bin in corresponding 
                                         //location
  
  matrix[86,num_loc_ifr] f_expanded; // population age distribution with ages 0 to 85+ 
                                     // as rows and location index as columns
  int loc_ind[length_dstar]; // the location index for each death bin
  vector[length_rstar] pi_weights_total; // weights for calculating location total 
                                         // seroprevalence
  vector[length_rstar] pi_weights_ag; // weights for aggregating seroprevalence age bins 
                                      // to death age bins
  
  
  real ifr_prior[length_dstar]; // IFR_{\ell,A}^\text{prior} 
}

parameters {
  // Seroprevalence
  vector<lower=0, upper=1>[length_rstar] pi_A; // seroprevalence for each location
  
  // Test characteristics
  vector<lower=0, upper=1>[num_test] sens; // sensitivity for each test
  vector<lower=0, upper=1>[num_test] spec; // specificity for each test
  
  // IFR
  vector<lower=0, upper=1>[length_dstar] ifr_A; // IFR for each location/age
}

model {
  vector[length_rstar] p_A; // test positivity 
  vector[length_dstar] pi_ag; // seroprevalence aggregated to death age bins
  
  // Positivity //
  p_A = sens[study_match_pi] .* pi_A + 
        (1 - spec[study_match_pi]) .* (1-pi_A); 
        
  // Average seroprevalence to match death age bins
  for (i in 1:length_dstar) {
    pi_ag[i] = sum(pi_A[min_match_sero_to_death[i]:max_match_sero_to_death[i]].* 
            pi_weights_ag[min_match_sero_to_death[i]:max_match_sero_to_death[i]]);
  }
  
  // Model //
  D_star ~ poisson(N .* pi_ag .* ifr_A);
  R_star ~ binomial(n, p_A); 
  
  // Priors //
    
  // Prev
  pi_A ~ beta(2,6); 
  
  // IFR
  ifr_A ~ beta(1,ifr_prior);
  
  // Test characteristics
  sens_x ~ binomial(sens_n, sens);
  spec_x ~ binomial(spec_n, spec);
  
  sens ~ beta(10,1);
  spec ~ beta(50, 1); 
}

generated quantities {
  vector[length_dstar] pi_ag;
  vector[num_loc_all] pi_bar;
        
  // Average seroprevalence to match death age bins
  for (i in 1:length_dstar) {
    pi_ag[i] = sum(pi_A[min_match_sero_to_death[i]:max_match_sero_to_death[i]].* 
            pi_weights_ag[min_match_sero_to_death[i]:max_match_sero_to_death[i]]);
  }
  
  // Get total location seroprevalence
  for (i in 1:num_loc_all) {
    pi_bar[i] = sum(pi_A[min_match_total_sero[i]:max_match_total_sero[i]] .*
                pi_weights_total[min_match_total_sero[i]:max_match_total_sero[i]]);
  }
}
