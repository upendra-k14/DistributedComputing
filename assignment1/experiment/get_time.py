import oddeven
import alternative_sort
import asasaski
import pickle
from statistics import mean

if __name__ == "__main__":

    n_list = [1000]
    a1_time_list = []
    a2_time_list = []
    a3_time_list = []

    for n in n_list:
        l = pickle.load(open("Sample/{}_samples.p".format(n),"rb"))
        t1 = []
        t2 = []
        t3 = []
        print("h")
        for x in l:
            t1.append(oddeven.main(given_array=x))
            t2.append(asasaski.main(given_array=x))
            t3.append(alternative_sort.main(given_array=x))
        a1_time_list.append(mean(t1))
        a2_time_list.append(mean(t2))
        a3_time_list.append(mean(t3))

    print(a1_time_list)
    print(a2_time_list)
    print(a3_time_list)
