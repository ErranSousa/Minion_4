import pickle

# OXYBase Continuous Loop
run_oxy_pickle_name = '/home/pi/Documents/Minion_scripts/run_oxy_state.pickle'

# Create and update a pickle file.  This file tracks if the loop should be running.
run_oxy = False
with open(run_oxy_pickle_name, 'wb') as pickle_file_fid:
    pickle.dump(run_oxy, pickle_file_fid)
