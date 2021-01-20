#################################################
# V21 - Author: Asaf Ravid <asaf.rvd@gmail.com> #
#################################################


import sss
import numpy as np
import csv
import os
import sss_diff



# Reuse:
# sss.sss_run(sectors_list=[], build_csv_db_only=0, build_csv_db=0, csv_db_path='None', read_united_states_input_symbols=0, tase_mode=0, num_threads=1, market_cap_included=1, use_investpy=0, research_mode=0, profit_margin_limit=0.17, ev_to_cfo_ratio_limit = 100.0, best_n_select=50, enterprise_value_to_revenue_limit=15, generate_result_folders=1)

# Run Build DB Only: Nasdaq100/S&P500
# ===================================
# sss.sss_run(sectors_list=[], build_csv_db_only=1, build_csv_db=1, csv_db_path='None', read_united_states_input_symbols=0, tase_mode=0, num_threads=20, market_cap_included=1, use_investpy=0, research_mode=0, profit_margin_limit=0.12, ev_to_cfo_ratio_limit = 100.0, best_n_select=3, enterprise_value_to_revenue_limit=20, generate_result_folders=1)

# Run Build DB Only: All/Others
# =============================
# sss.sss_run(sectors_list=[], build_csv_db_only=1, build_csv_db=1, csv_db_path='None', read_united_states_input_symbols=1, tase_mode=0, num_threads=20, market_cap_included=1, use_investpy=0, research_mode=0, profit_margin_limit=0.10, ev_to_cfo_ratio_limit = 100.0, best_n_select=3, enterprise_value_to_revenue_limit=20, generate_result_folders=1)

# Run Build DB Only: TASE
# =============================
# sss.sss_run(sectors_list=[], build_csv_db_only=1, build_csv_db=1, csv_db_path='None', read_united_states_input_symbols=0, tase_mode=1, num_threads=20, market_cap_included=1, use_investpy=0, research_mode=0, profit_margin_limit=0.10, ev_to_cfo_ratio_limit = 100.0, best_n_select=3, enterprise_value_to_revenue_limit=25, generate_result_folders=1)


# Research Mode:
# ==============
def prepare_appearance_counters_dictionaries(csv_db_path, appearance_counter_dict_ssss, appearance_counter_dict_sssss):
    csv_db_filename = csv_db_path + '/db.csv'
    with open(csv_db_filename, mode='r', newline='') as engine:
        reader = csv.reader(engine, delimiter=',')
        row_index = 0
        for row in reader:
            if row_index <= 1:  # first row is just a title of evr and pm, then a title of columns
                row_index += 1
                continue
            else:
                appearance_counter_dict_ssss[ (row[0],row[1],row[2],float(row[4]))] = 0.0  # Symbol, Short Name, Sector, SSSS  Value
                appearance_counter_dict_sssss[(row[0],row[1],row[2],float(row[5]))] = 0.0  # Symbol, Short Name, Sector, SSSSS Value


def research_db(min_evr, max_evr, pm_min, pm_max, csv_db_path, read_united_states_input_symbols, tase_mode, generate_result_folders, appearance_counter_min, appearance_counter_max):
    appearance_counter_dict_ssss  = {}
    appearance_counter_dict_sssss = {}
    prepare_appearance_counters_dictionaries(csv_db_path, appearance_counter_dict_ssss, appearance_counter_dict_sssss)
    research_rows_ssss  = np.zeros( (max_evr-min_evr+1, pm_max-pm_min+1), dtype=int )
    research_rows_sssss = np.zeros( (max_evr-min_evr+1, pm_max-pm_min+1), dtype=int )
    for enterprise_value_to_revenue_limit in range(min_evr,max_evr+1):
        for profit_margin_limit in range(pm_min,pm_max+1):
            num_results_for_evr_and_pm = sss.sss_run(sectors_list=[], build_csv_db_only=0, build_csv_db=0, csv_db_path=csv_db_path, read_united_states_input_symbols=read_united_states_input_symbols, tase_mode=tase_mode, num_threads=1, market_cap_included=1, use_investpy=0, research_mode=1, profit_margin_limit=float(profit_margin_limit)/100.0, ev_to_cfo_ratio_limit = 100.0, best_n_select=3, enterprise_value_to_revenue_limit=enterprise_value_to_revenue_limit, generate_result_folders=generate_result_folders, appearance_counter_dict_ssss=appearance_counter_dict_ssss, appearance_counter_dict_sssss=appearance_counter_dict_sssss, appearance_counter_min=appearance_counter_min, appearance_counter_max=appearance_counter_max)
            if num_results_for_evr_and_pm < 1: break  # already 0 results. With higher profit margin limit there will still be 0
            research_rows_ssss[ enterprise_value_to_revenue_limit-min_evr][profit_margin_limit-pm_min] = int(num_results_for_evr_and_pm)
            research_rows_sssss[enterprise_value_to_revenue_limit-min_evr][profit_margin_limit-pm_min] = int(num_results_for_evr_and_pm)
            print('row {:3} -> (enterprise_value_to_revenue_limit {:3}) | col {:3} -> (profit_margin_limit {:3}%): num_results_for_evr_and_pm = {}'.format(enterprise_value_to_revenue_limit-min_evr, enterprise_value_to_revenue_limit, profit_margin_limit-pm_min, profit_margin_limit, num_results_for_evr_and_pm))
    results_filename    = 'results_evr{}-{}_pm{}-{}.csv'.format(min_evr,max_evr,pm_min,pm_max)
    np.savetxt(csv_db_path+'/'+results_filename,  research_rows_ssss.astype(int), fmt='%d', delimiter=',')
    title_row = list(range(pm_min,pm_max+1))
    title_row.insert(0, 'evr / pm')
    evr_rows_pm_cols_filenames_list = [csv_db_path+'/'+results_filename]
    # Read Results, and add row and col axis:
    for filename in evr_rows_pm_cols_filenames_list:
        evr_rows_pm_cols = [title_row]
        with open(filename, mode='r', newline='') as engine:
            reader = csv.reader(engine, delimiter=',')
            row_index = 0
            for row in reader:
                row.insert(0, min_evr+row_index)
                evr_rows_pm_cols.append(row)
                row_index += 1
    for index in range(len(evr_rows_pm_cols_filenames_list)):
        row_col_csv_filename = evr_rows_pm_cols_filenames_list[index].replace('.csv','_evr_row_pm_col.csv')
        os.makedirs(os.path.dirname(row_col_csv_filename), exist_ok=True)
        with open(row_col_csv_filename, mode='w', newline='') as engine:
            writer = csv.writer(engine)
            writer.writerows(evr_rows_pm_cols)

    sorted_appearance_counter_dict_ssss         = {k: v for k, v in sorted(appearance_counter_dict_ssss.items(), key=lambda item: item[1], reverse=True)}
    result_sorted_appearance_counter_dict_ssss  = {k: v for k, v in sorted_appearance_counter_dict_ssss.items() if v > 0.0}

    sorted_appearance_counter_dict_sssss        = {k: v for k, v in sorted(appearance_counter_dict_sssss.items(), key=lambda item: item[1], reverse=True)}
    result_sorted_appearance_counter_dict_sssss = {k: v for k, v in sorted_appearance_counter_dict_sssss.items() if v > 0.0}

    recommendation_list_filename_ssss = csv_db_path+'/recommendation_ssss_'+results_filename.replace('results_','')
    with open(recommendation_list_filename_ssss, 'w') as f:
        f.write("Ticker,Name,Sector,ssss_value,appearance_counter\n")
        for key in result_sorted_appearance_counter_dict_ssss.keys():
            f.write("%s,%s,%s,%s,%s\n"%(key[0],str(key[1]).replace(',',' '),key[2],key[3],result_sorted_appearance_counter_dict_ssss[key]))

    recommendation_list_filename_sssss = csv_db_path+'/recommendation_sssss_'+results_filename.replace('results_','')
    with open(recommendation_list_filename_sssss, 'w') as f:
        f.write("Ticker,Name,Sector,sssss_value,appearance_counter\n")
        for key in result_sorted_appearance_counter_dict_sssss.keys():
            f.write("%s,%s,%s,%s,%s\n"%(key[0],str(key[1]).replace(',',' '),key[2],key[3],result_sorted_appearance_counter_dict_sssss[key]))

# TASE:
# =====
# research_db(min_evr=1, max_evr=25, pm_min=5,  pm_max=45, csv_db_path='Results/20210117-021721_Tase_FavorTechBy3_MCap_pm0.0567_evr15.0_BuildDb_nResults438',   read_united_states_input_symbols=0, tase_mode=1, generate_result_folders=0, appearance_counter_min=5, appearance_counter_max=55)

# NASDAQ100+S&P500+RUSSEL1000:
# ============================
# research_db(min_evr=1, max_evr=45, pm_min=5, pm_max=50, csv_db_path='Results/20210116-220250_FavorTechBy3_MCap_pm0.17_evr17.5_BuildDb_nResults1083',         read_united_states_input_symbols=0, tase_mode=0, generate_result_folders=0, appearance_counter_min=5, appearance_counter_max=55)

# Generate:
# research_db(min_evr=6, max_evr=6,  pm_min=19, pm_max=19, csv_db_path='Results/20210116-220250_FavorTechBy3_MCap_pm0.17_evr17.5_BuildDb_nResults1083',         read_united_states_input_symbols=0, tase_mode=0, generate_result_folders=1, appearance_counter_min=20, appearance_counter_max=40)

# ALL:
# ====
# research_db(min_evr=1, max_evr=55, pm_min=5, pm_max=45, csv_db_path='Results/20210117-150719_FavorTechBy3_All_MCap_pm0.24_evr15.0_BuildDb_nResults6501',  read_united_states_input_symbols=1, tase_mode=0, generate_result_folders=0, appearance_counter_min=5, appearance_counter_max=55)
sss_diff.run(newer_path='Results/20210117-150719_FavorTechBy3_All_MCap_pm0.24_evr15.0_BuildDb_nResults6501', older_path='Results/20210111-231110_FavorTechBy3_All_MCap_pm0.24_evr15.0_BuildDb_nResults8724', db_exists_in_both_folders=1, diff_only_recommendation=1, ticker_index=0, name_index=1, movement_threshold=3, newer_rec=[1,55,5,45], older_rec=[1,45,5,45], rec_length=60)

# Generate ALL:
# research_db(min_evr=7, max_evr=7, pm_min=32, pm_max=32, csv_db_path='Results/20210117-150719_FavorTechBy3_All_MCap_pm0.24_evr15.0_BuildDb_nResults6501',  read_united_states_input_symbols=1, tase_mode=0, generate_result_folders=1, appearance_counter_min=20, appearance_counter_max=40)


# Comparisons:
# sss_diff.run(newer_path='', older_path='', db_exists_in_both_folders=1, ticker_index=0, name_index=1, movement_threshold=3, rec_pm_min=1, rec_ever_max=55, rec_pm_min=5, rec_pm_max=45)
