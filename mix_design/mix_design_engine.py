def mix_design(data):
    # -----------------------------
    # INPUTS
    # -----------------------------
    grade = data.get("grade")
    exposure = data.get("exposure")
    slump = data.get("slump")
    max_agg_size = data.get("max_agg_size")

    sg_cement = data.get("sg_cement")
    sg_fa = data.get("sg_fa")
    sg_ca = data.get("sg_ca")

    mc_fa = data.get("mc_fa")
    mc_ca = data.get("mc_ca")

    wa_fa = data.get("wa_fa")
    wa_ca = data.get("wa_ca")

    mineral_percent = data.get("mineral_percent", 0)
    chemical_percent = data.get("chemical_percent", 0)

    # -----------------------------
    # TARGET MEAN STRENGTH
    # -----------------------------
    grade_value = int(grade.replace("M", ""))
    std_dev = 5  # assumed
    target_mean_strength = grade_value + 1.65 * std_dev

    # -----------------------------
    # WATER CONTENT (approx)
    # -----------------------------
    base_water = 186 if max_agg_size == 20 else 170

    # slump correction
    base_water += (slump - 50) * 0.3

    # moisture correction
    final_water = base_water * (1 + (mc_fa - wa_fa)/100 + (mc_ca - wa_ca)/100)

    # -----------------------------
    # WATER-CEMENT RATIO (assumed)
    # -----------------------------
    wc_ratio = 0.5 if grade_value >= 30 else 0.55

    # durability limits (simplified)
    wc_limit_map = {
        "mild": 0.55,
        "moderate": 0.50,
        "severe": 0.45,
        "very severe": 0.45,
        "extreme": 0.40
    }

    wc_limit = wc_limit_map.get(exposure.lower(), 0.5)

    # -----------------------------
    # CEMENT CALCULATION
    # -----------------------------
    cement = final_water / wc_ratio

    # enforce minimum cement = 300
    if cement < 300:
        cement = 300

    # -----------------------------
    # ADMIXTURES
    # -----------------------------
    mineral_admixture = cement * (mineral_percent / 100)
    chemical_admixture = cement * (chemical_percent / 100)

    total_cementitious = cement + mineral_admixture

    # -----------------------------
    # WATER-BINDER RATIO
    # -----------------------------
    wb_ratio = final_water / total_cementitious

    # -----------------------------
    # AGGREGATES (simplified)
    # -----------------------------
    coarse_agg = 1200 * (1 - (slump / 300))
    fine_agg = 700 * (1 + (slump / 500))

    # -----------------------------
    # MIX RATIO
    # -----------------------------
    mix_ratio = f"1 : {round(fine_agg/cement,2)} : {round(coarse_agg/cement,2)}"

    # -----------------------------
    # WARNINGS
    # -----------------------------
    warning = None

    if wc_ratio > wc_limit:
        warning = "Warning: w/c exceeds durability limit"
    elif wb_ratio > wc_limit:
        warning = "Warning: w/b exceeds durability limit"

    # -----------------------------
    # FINAL RESPONSE (FIXED FORMAT)
    # -----------------------------
    return {
        "target_mean_strength": round(target_mean_strength, 2),

        "water": {
            "base": round(base_water, 2),
            "final": round(final_water, 2)
        },

        "cement": round(cement, 2),
        "mineral_admixture": round(mineral_admixture, 2),
        "total_cementitious": round(total_cementitious, 2),
        "chemical_admixture": round(chemical_admixture, 2),

        "aggregates": {
            "fine": round(fine_agg, 2),
            "coarse": round(coarse_agg, 2)
        },

        "ratios": {
            "w_c": round(wc_ratio, 3),
            "w_b": round(wb_ratio, 3)
        },

        "mix_ratio": mix_ratio,
        "warning": warning
    }