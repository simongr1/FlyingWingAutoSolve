def lift_cost(v_sqrd,v_old,lift_weight, L0,mass):
    #set v_sqrd and v_old to one if you just wnat to calculate the current cost
    return lift_weight*(-1/(0.05* mass*9.81)*(L0*v_sqrd/(v_old**2) - mass*9.81))**2
def trim_cost(v_sqrd,v_old,trim_weight,M0):
    #set v_sqrd and v_old to one if you just wnat to calculate the current cost
    return trim_weight*(M0*v_sqrd/(v_old**2))**2
def power_cost(v_sqrd,v_old,power_weight,powerBattery,D0):
    powerRequired=D0*v_sqrd**(3/2) / (v_old**2)
    print(powerRequired)
    if powerBattery > powerRequired:
        return 0
    else:
        return power_weight*(-1/(0.1*powerBattery) *(powerRequired-powerBattery))**2
def static_margin_cost(SM_weight,SMGoal,staticMargin):
    return SM_weight*(-1/(0.05)*(staticMargin-SMGoal))**2 #allow the static margin to be between 0.07 and 0.17
def f_velocity_min(v_sqrd,v_old,M0,L0,D0,totalMass,powerBattery,trim_weight,lift_weight,power_weight):
    return trim_cost(v_sqrd,v_old,trim_weight,M0)+lift_cost(v_sqrd,v_old,lift_weight,L0,totalMass)+power_cost(v_sqrd,v_old,power_weight,powerBattery,D0)
