use "data\house.dta", clear

forvalues i=2000/2008 {
	gen year`i'= 1 if year == `i'
	replace year`i'=0 if year != `i'
	gen year`i'_delta_tax_eff = year`i'*delta_tax_eff
}

forvalues i = 10(10)90 {
	preserve
	eststo quant_est_`i': qui mmqreg  ln_real_price year2005_delta_tax_eff year2006_delta_tax_eff year2007_delta_tax_eff year2008_delta_tax_eff ln_prop_value, absorb(year kommune_old_id) quantile(`i') cluster(index)
	
	// Save estimates to matrix 
	mat B = r(table)
	mat B = B'
	
	// Overwrite current datasets with said matrix
	// This will have all estimates saved - including upper/lower bound 
	clear
	svmat B, names(col)
	
	// Only keep estimates of the 2005-2008 year-coefficients
	// NB! No way in Stata to keep varnames when doing this. If the order of the varnames in the regression is changed, you need to change which observation to keep
	keep if inrange(_n, 13, 16)
	
	// Save varname
	egen varname = seq(), from(2005) to(2008) 
	
	// Make it clear which quantile is estimated
	gen q = `i'
	replace q = q/100
	order q, first
	save models\quant_est_`i', replace
	restore
}

esttab using "tabs\stata_raw.tex", style(tex) replace star(* 0.10 ** 0.05 *** 0.01) se b(%5.3f) substitute({l} {p{\linewidth}})


***************************************
*** W trend diff? 2004 as base year****
***************************************
eststo clear

forvalues i = 10(10)90 {
	preserve
	eststo quant_est_`i': qui mmqreg  ln_real_price  year2000_delta_tax_eff year2001_delta_tax_eff year2002_delta_tax_eff year2003_delta_tax_eff year2005_delta_tax_eff year2006_delta_tax_eff year2007_delta_tax_eff year2008_delta_tax_eff ln_prop_value, absorb(year kommune_old_id) quantile(`i') cluster(index)
	
	// Save estimates to matrix 
	mat B = r(table)
	mat B = B'

	// Overwrite current datasets with said matrix
	// This will have all estimates saved - including upper/lower bound 
	clear
	svmat B, names(col)
	
	// Only keep estimates of the 2000-2003 & 2005-2008 year-coefficients
	keep if inrange(_n, 21, 28) 
	
	// Give name
	egen varname = seq(), from(2000) to(2008) 
	forvalues j = 5/8 {
		replace varname = varname+1 if _n == `j'
	}
	
	// Make it clear which quantile is estimated
	gen q = `i'
	replace q = q/100
	order q, first
	save models\trend_diff\quant_est_`i'_trend_diff_04, replace
	restore
}

esttab using "tabs\stata_main_qreg_raw.tex", style(tex) replace star(* 0.10 ** 0.05 *** 0.01) se b(%5.3f) substitute({l} {p{\linewidth}})

******************************************************************
**W trend diff? 2004 as base year, restricting 2000-2002 to zero**
******************************************************************
eststo clear
forvalues i = 10(10)90 {
	preserve
	eststo quant_est_`i': qui mmqreg  ln_real_price year2003_delta_tax_eff year2005_delta_tax_eff year2006_delta_tax_eff year2007_delta_tax_eff year2008_delta_tax_eff ln_prop_value, absorb(year kommune_old_id) quantile(`i') cluster(index)
	
	// Save estimates to matrix 
	mat B = r(table)
	mat B = B'

	// Overwrite current datasets with said matrix
	// This will have all estimates saved - including upper/lower bound 
	clear
	svmat B, names(col)
	
	// Only keep estimates of the 2003 & 2005-2008 year-coefficients
	keep if inrange(_n, 15, 19) 
	
	// Give name
	egen varname = seq(), from(2003) to(2008) 
	forvalues j = 2/5 {
		replace varname = varname+1 if _n == `j'
	}
	
	// Make it clear which quantile is estimated
	gen q = `i'
	replace q = q/100
	order q, first
	save models\trend_diff\quant_est_`i'_trend_diff_04_restrict00to02, replace
	restore
}

*************************************
** W trend diff? 2003 as base year **
*************************************
eststo clear

forvalues i = 10(10)90 {
	preserve
	eststo quant_est_`i': qui mmqreg  ln_real_price year2000_delta_tax_eff year2001_delta_tax_eff year2002_delta_tax_eff year2004_delta_tax_eff year2005_delta_tax_eff year2006_delta_tax_eff year2007_delta_tax_eff year2008_delta_tax_eff ln_prop_value, absorb(year kommune_old_id) quantile(`i') cluster(index)
	
	// Save estimates to matrix 
	mat B = r(table)
	mat B = B'

	// Overwrite current datasets with said matrix
	// This will have all estimates saved - including upper/lower bound 
	clear
	svmat B, names(col)
	
	// Only keep estimates of the 2000-2002 & 2004-2008 year-coefficients
	keep if inrange(_n, 21, 28) 
	
	// Give name
	egen varname = seq(), from(2000) to(2008) 
	forvalues j = 4/8 {
		replace varname = varname+1 if _n == `j'
	}
	
	// Make it clear which quantile is estimated
	gen q = `i'
	replace q = q/100
	order q, first
	save models\trend_diff\quant_est_`i'_trend_diff_03, replace
	restore
}

***************************************
*** W trend diff? 2004 as base year****
***************************************
eststo clear

forvalues i = 10(10)90 {
	preserve
	eststo quant_est_`i': qui mmqreg  ln_real_price  year2000_delta_tax_eff year2001_delta_tax_eff year2002_delta_tax_eff year2003_delta_tax_eff year2005_delta_tax_eff year2006_delta_tax_eff year2007_delta_tax_eff year2008_delta_tax_eff ln_prop_value, absorb(year kommune_old_id) quantile(`i') cluster(index)
	
	// Save estimates to matrix 
	mat B = r(table)
	mat B = B'

	// Overwrite current datasets with said matrix
	// This will have all estimates saved - including upper/lower bound 
	clear
	svmat B, names(col)
	
	// Only keep estimates of the 2000-2003 & 2005-2008 year-coefficients
	keep if inrange(_n, 21, 28) 
	
	// Give name
	egen varname = seq(), from(2000) to(2008) 
	forvalues j = 5/8 {
		replace varname = varname+1 if _n == `j'
	}
	
	// Make it clear which quantile is estimated
	gen q = `i'
	replace q = q/100
	order q, first
	save models\trend_diff\quant_est_`i'_trend_diff_04, replace
	restore
}