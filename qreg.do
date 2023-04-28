clear all
cls
cd "C:\Users\JBH\Dropbox\11_semester\Public_Econ_seminar"

use "data\house.dta", clear

xtset id

keep if year >= 2000
keep if year <= 2008

gen year05 = 1 if year == 2005
replace year05 = 0 if year != 2005
gen year06 = 1 if year == 2006
replace year06 = 0 if year!= 2006
gen year07 = 1 if year == 2007
replace year07 = 0 if year != 2007
gen year08 = 1 if year == 2008
replace year08 = 0 if year != 2008

gen year05_delta_tax_eff = year05*delta_tax_eff 
gen year06_delta_tax_eff = year06*delta_tax_eff 
gen year07_delta_tax_eff = year07*delta_tax_eff 
gen year08_delta_tax_eff = year08*delta_tax_eff 

// xtqreg ln_real_price year05_delta_tax_eff year06_delta_tax_eff year07_delta_tax_eff year08_delta_tax_eff ln_prop_value i.year, i(kommune_old_id) quantile(.1(0.1)0.9)

eststo quant_est: mmqreg  ln_real_price year05_delta_tax_eff year06_delta_tax_eff year07_delta_tax_eff year08_delta_tax_eff ln_prop_value, absorb(year kommune_old_id) quantile(.1(0.1)0.9)

esttab using "tabs\stata_raw.tex", style(tex) mtitle("Something" "lol") replace star(* 0.10 ** 0.05 *** 0.01) se b(%5.3f)