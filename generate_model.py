import os
import time

estimated_demand = [[100, 250, 95, 160],
                    [150, 143, 195, 99],
                    [135, 80, 242, 55],
                    [83, 225, 111, 96],
                    [120, 210, 70, 115],
                    [230, 98, 124, 80]]

hire_return_rate = [[0.60, 0.20, 0.10, 0.10],
                    [0.15, 0.55, 0.25, 0.05],
                    [0.15, 0.20, 0.54, 0.11],
                    [0.08, 0.12, 0.27, 0.53]]

transfer_cost = [[0, 20, 30, 50],
                 [20, 0, 15, 35],
                 [30, 15, 0, 25],
                 [50, 35, 25, 0]]

hire_price = [[50, 70],
              [0, 0],
              [120, 150]]

sat_discount = 20
marginal_cost = [20, 99999, 30]
rent_days = [1, 3]
days = [0, 1, 2, 3, 4, 5]
sat = days[-1]
days_name = ["mon", "tues", "wed", "thurs", "fri", "sat"]
depots = ["g", "m", "b", "p"]
damaged_car_charge = 100
damage_percentage = 0.10
repair_capacity_increase = 5

P = {
    "g" : 0,
    "m" : 1,
    "b" : 2,
    "p" : 3
}

D = {
    "g" : 0,
    "m" : 1,
    "b" : 2,
    "p" : 3,
}

Q = {
    1 : 0.55,
    2 : 0,
    3 : 0.25
}

rp = {
    "g" : "0",
    "m" : "12",
    "b" : "20",
    "p" : "0"
}

def main():
    start = time.process_time()

    if os.path.exists("final.lp"):
        os.remove("final.lp")

    f = open("final.lp", "a")
    #-----------------------------------------------------------
    # Objective Funtion
    f.write("max: " )
    for i in depots:
        for t in days:
            if t != 5:
                for k in rent_days:
                    # SUM[i=[Glasgow, Manchester, Birmingham, Plymouth], t=Monday to Friday, k=1 to 3] P_iiQ_k(RCA_k-CS_k+10)tr_it
                    f.write(str(hire_return_rate[P[i]][P[i]] * Q[k] * (hire_price[k-1][0] - marginal_cost[k-1] + (damage_percentage * damaged_car_charge))) + "*tr_" + i + days_name[t] + " + ")

    for i in depots:
        for t in days:
            if t != 5: 
                for k in rent_days:
                    for j in depots:
                        if i != j:
                            # SUM[i=[Glasgow, Manchester, Birmingham, Plymouth], j=[Glasgow, Manchester, Birmingham, Plymouth], t=Monday to Friday, k=1 to 3] P_ij*Q_k*(RCA_k-CS_k+10)*tr_it
                            f.write(str(hire_return_rate[P[i]][P[j]] * + Q[k] * (hire_price[k-1][1] - marginal_cost[k-1] + (damage_percentage * damaged_car_charge))) + "*tr_" + i + days_name[t] + " + ") 

    for i in depots:
        # SUM[i=[Glasgow, Manchester, Birmingham, Plymouth], t=Saturday] P_iiQ_1(RCC-CS_1+10)tr_it
        f.write(str(hire_return_rate[P[i]][P[i]] * Q[1] * (hire_price[0][0] - sat_discount - marginal_cost[0] + (damage_percentage * damaged_car_charge))) + "*tr_" + i + days_name[sat] + " + ")

    for i in depots:
        for j in depots:
            if i != j:
                # SUM[i=[Glasgow, Manchester, Birmingham, Plymouth], t=Saturday] P_ijQ_1(RCD-CS_1+10)tr_it
                f.write(str(hire_return_rate[P[i]][P[j]] * Q[1] * (hire_price[0][1] - sat_discount - marginal_cost[0] + (damage_percentage * damaged_car_charge))) + "*tr_" + i + days_name[sat] + " + ")

    for i in depots:
        for k in rent_days:
            if k != 1:
                # SUM[i=[Glasgow, Manchester, Birmingham, Plymouth], t=Saturday, k=2 to 3] P_iiQ_k(RCA_k-CS_k+10)tr_it
                f.write(str(hire_return_rate[P[i]][P[i]] * Q[k] * (hire_price[k-1][0] - marginal_cost[k-1] + (damage_percentage * damaged_car_charge))) + "*tr_" + i + days_name[sat] + " + ") 

    for i in depots:
        for j in depots:
            for k in rent_days:
                if k != 1 and i != j:
                            # SUM[i=[Glasgow, Manchester, Birmingham, Plymouth], j=[Glasgow, Manchester, Birmingham, Plymouth], t=Saturday, k=2 to 3] P_ij*Q_k(RCB_k-CS_k+10)*tr_it
                            f.write(str(hire_return_rate[P[i]][P[j]] * Q[k] * (hire_price[k-1][1] - marginal_cost[k-1] + (damage_percentage * damaged_car_charge))) + "*tr_" + i + days_name[sat] + " + ") 

    # To get rid of unwarranted sign and prep for subtraction
    f.write("0 - ")

    for i in depots:
        for j in depots:
            for t in days:
                if i != j:
                    # SUM[i=[Glasgow, Manchester, Birmingham, Plymouth], j=[Glasgow, Manchester, Birmingham, Plymouth] C_ij*tu_ijt]
                    f.write(str(transfer_cost[P[i]][P[j]]) + "*tu_" + i + j + days_name[t] + " - ")

    for i in depots:
        for j in depots:
            for t in days:
                if i != j:
                    # SUM[i=[Glasgow, Manchester, Birmingham, Plymouth], j=[Glasgow, Manchester, Birmingham, Plymouth] C_ij*td_ijt]
                    f.write(str(transfer_cost[P[i]][P[j]]) + "*td_" + i + j + days_name[t] + " - ")              

    f.write("15n;")

    f.write("\n\n")

    f.write("/* Constraints */")
    #-----------------------------------------------------------
    f.write("\n" + "// Constraint 1: Total number of undamaged cars into depot i on day t\n")
    for i in depots:
        for t in days:
            for j in depots:
                for k in rent_days:
                    # SUM[j=[Glasgow, Manchester, Birmingham, Plymouth], k=1 to 3] 0.9*P_ji*Q_k*tr_jt-k
                    f.write(str(0.9 * hire_return_rate[P[j]][P[i]] * Q[k]) + "*tr_" + j + days_name[t-k] + " + ")
            
            for j in depots:
                # SUM[j=[Glasgow, Manchester, Birmingham, Plymouth]] tu_jit-1
                if i != j: 
                    f.write("tu_" + j + i + days_name[t-1] + " + ")
                    
            # rp_it-1
            f.write("rp_" + i + days_name[t-1] + " + ")

            # eu_it-1
            f.write("eu_" + i + days_name[t-1] + " + ")

            # = nu_it
            f.write("0 = nu_" + i + days_name[t] + ";\n")

    #-----------------------------------------------------------
    f.write("\n" + "// Constraint 2: Total number of damaged cars into depot i on day t\n")
    for i in depots:
        for t in days:
            for j in depots:
                for k in rent_days:
                    # SUM[j=[Glasgow, Manchester, Birmingham, Plymouth], k=1 to 3] 0.1*P_ji*Q_k*tr_jt-k
                    f.write(str(0.1 * hire_return_rate[P[j]][P[i]] * Q[k]) + "*tr_" + j + days_name[t-k] + " + ")
            
            for j in depots:
                # SUM[j=[Glasgow, Manchester, Birmingham, Plymouth]] td_jit-1
                if i != j: 
                    f.write("td_" + j + i + days_name[t-1] + " + ")

            # ed_it-1
            f.write("ed_" + i + days_name[t-1] + " + ")

            # = nd_it
            f.write("0 = nd_" + i + days_name[t] + ";\n")

    #-----------------------------------------------------------
    f.write("\n" + "// Constraint 3: Total number of undamaged cars out of depot i on day t\n")
    # Removed rp_it-1 as it causes model to be infeasible, namely it is already counted within tu_ijt(cars to be transfered on day t from i to j)
    # hence no need for rp_it-1.
    for i in depots:
        for t in days:
            # tr_it
            f.write("tr_" + i + days_name[t] + " + ")

            for j in depots:
                if i != j:
                    # SUM[j=[Glasgow, Manchester, Birmingham, Plymouth]] tu_ijt
                    f.write("tu_" + i + j + days_name[t] + " + ")

            # eu_it
            f.write("eu_" + i + days_name[t] + " + ")

            # = nu_it
            f.write("0 = nu_" + i + days_name[t] + ";\n")

    #-----------------------------------------------------------
    f.write("\n" + "// Constraint 4: Total number of damaged cars out of depot i on day t\n")
    for i in depots:
        for t in days:
            # rp_it-1
            f.write("rp_" + i + days_name[t-1] + " + ")

            for j in depots:
                if i != j:
                    # SUM[j=[Glasgow, Manchester, Birmingham, Plymouth]] td_ijt
                    f.write("td_" + i + j + days_name[t] + " + " )

            # ed_it
            f.write("ed_" + i + days_name[t] + " + ")

            # = nd_it
            f.write("0 = nd_" + i + days_name[t] + ";\n")

    #-----------------------------------------------------------
    f.write("\n" + "// Constraint 5: Repair capacity of depot i on all days\n")
    for i in depots:
        for t in days:
            # rp_it
            f.write("rp_" + i + days_name[t])

            # <= R_i
            f.write(" <= " + rp[i] + ";\n")

    #-----------------------------------------------------------
    f.write("\n" + "// Constraint 6: Demand at depot i on day t\n")
    for i in depots:
        for t in days:
            # tr_it
            f.write("tr_" + i + days_name[t])

            # <= D_it
            f.write(" <= " + str(estimated_demand[t][D[i]]) + ";\n")

    #-----------------------------------------------------------
    f.write("\n" + "// Constraint 7: Total number of cars equals number hired out from all depots on Monday" + 
            "for 3 days, plus those on Tuesday for 3 days, plus all damaged and undamaged cars in depots" + 
            "at the beginning of Wednesday.\n")
    for i in depots:
        f.write(str(Q[3]) + "*tr_" + i + "mon + " + str(Q[3]) + "*tr_" + i + "tues + nu_" + i + "wed + nd_" + i + "wed" + " + ")
    f.write("0 = n;")

    f.close()

    print(time.process_time() - start)

if __name__ == "__main__":
    main()