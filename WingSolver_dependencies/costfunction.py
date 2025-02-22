def lift_cost(v_sqrd,v_old,lift_weight, L0,mass):
    #set v_sqrd and v_old to one if you just wnat to calculate the current cost
    return lift_weight*(-1/(0.01* mass*9.81)*(L0*v_sqrd/(v_old**2) - mass*9.81))**2
def trim_cost(v_sqrd,v_old,trim_weight,M0):
    #set v_sqrd and v_old to one if you just wnat to calculate the current cost
    return trim_weight*(2*M0*v_sqrd/(v_old**2))**2
def drag_cost(v_sqrd,v_old,drag_weight,D0):
    #set v_sqrd and v_old to one if you just wnat to calculate the current cost
    return drag_weight*(3*D0*v_sqrd/(v_old**2))**2
def static_margin_cost(SM_weight,SMGoal,staticMargin):
    return SM_weight*(-1/(0.1*SMGoal)*(staticMargin-SMGoal))**2 
def f_velocity_min(v_sqrd,v_old,M0,L0,totalMass,trim_weight,lift_weight):
    return trim_cost(v_sqrd,v_old,trim_weight,M0)+lift_cost(v_sqrd,v_old,lift_weight,L0,totalMass)
