use "data\house.dta", clear
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

forvalues i = 10(10)90 {
	preserve
	eststo quant_est_`i': mmqreg  ln_real_price year05_delta_tax_eff year06_delta_tax_eff year07_delta_tax_eff year08_delta_tax_eff ln_prop_value, absorb(year kommune_old_id) quantile(`i')
	
	// Save estimates to matrix 
	mat B = r(table)
	mat B = B'
	
	// Overwrite current datasets with said matrix - this all estimates in order of how it is written
	clear
	svmat B, names(col)
	
	// Only keep estimates of the 2007 year-coefficient (effect of reform). This is 'observation' 15 in matrix.
	// NB! No way in Stata to keep varnames when doing this. If the order of the varnames in the regression is changed, you need to change which observation to keep
	keep if _n == 15
	
	// Save varname
	gen varname = "year07_delta_tax_eff"
	
	// Make it clear which quantile is estimated
	gen q = `i'
	replace q = q/100
	order q, first
	save models\quant_est_`i', replace
	restore
}


esttab using "tabs\stata_raw.tex", style(tex) replace star(* 0.10 ** 0.05 *** 0.01) se b(%5.3f) substitute({l} {p{\linewidth}})