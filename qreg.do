cd "C:\Users\JBH\Dropbox\11_semester\Public_Econ_seminar"

use "data\house.dta"

xtset id

xtqreg ln_price delta_tax_eff eval_prop_2001 i.year, i(kommune_old_id) quantile(.1(0.1)0.9)