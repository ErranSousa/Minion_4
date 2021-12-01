import pickle
import sys
import os

pickle_file_name = "/home/pi/Documents/Minion_scripts/sampcount.pkl"

msg1 = "Sample Counter Reset Utility  "

print("-"*len(msg1))
print(msg1)
print("-"*len(msg1))


try:
    #Read out the current value
    countp = open(pickle_file_name,"rb")
    sampcount = pickle.load(countp)
    print("sampcount current value: " + str(sampcount))
    countp.close()
except:
    sys.exit(os.path.basename(__file__) + ": sampcount.pk1 file not found or open failed")


#Reset the value to zero
countp = open(pickle_file_name,"wb")
print("Resetting the Sample Counter to 0...")
sampcount = 0
pickle.dump(sampcount, countp)
countp.close()

#Verify
countp = open(pickle_file_name,"rb")
sampcount_verify = pickle.load(countp)
countp.close()
print("Verify sampcount: " + str(sampcount_verify))
if sampcount_verify == 0:
    print("Verify OK")
else:
    print("sampcount is not zero!")
