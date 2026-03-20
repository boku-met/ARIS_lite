![GitHub Tag](https://img.shields.io/github/v/tag/j-haacker/aris_lite)
![GitHub top language](https://img.shields.io/github/languages/top/j-haacker/aris_lite)
![GitHub License](https://img.shields.io/github/license/j-haacker/aris_lite)

# ARIS-lite

ARIS models plant growth based on environmental parameters. The model
draws on the references at the bottom.

## 🌱 state

The model has been validated against the original ARIS model. This is not
a stable software - future changes may break your work, but I will try
not to.
Canonical CLI namespace is now rooted at `aris`.
Legacy flat commands and legacy module-level `main*`/`cli` functions are
deprecated and will be removed in `0.4.0`.

## 🪛 usage

Small datasets (in-memory):
1. `aris 1go "winter wheat" "maize" input.zarr output.zarr`

Yearly staged processing:
1. `aris calc waterbudget -m snow 2019 2020 2021 2022 2023`
2. `aris calc pheno 2019 2020 2021 2022 2023`
3. `aris calc waterbudget -m soil 2019 2020 2021 2022 2023`
4. `aris calc yield -m both 2019 2020 2021 2022 2023 --yield-max <PATH> --yield-intercept <PATH> --yield-params <PATH>`

Notes:
- yearly path conventions default to `../data` and can be changed via `--base-dir`
- yield mode requires explicit parameter inputs (`--yield-max`, `--yield-intercept`, `--yield-params`)

Optional compatibility (deprecated until `0.4.0`): `aris-1go`,
`aris-calc-waterbudget`, `aris-calc-pheno`, `aris-calc-yield`.

## ✨ features

- calculate water up-take coefficients ("Kc factors") for winter wheat,
    spring barley, maize, soybean, norm potato, and grassland based on
    daily air surface temperature
- calculate soil water content and evapotranspiration
- compute daily crop-specific stress index based on maximum surface air
    temperature and soil water saturation
- estimate crop-specific yield depression (%) from stress indicators

## 📑 API documentation

<https://aris-lite.readthedocs.io>

## 🔗 dependencies

- dask, numpy, pandas, snowmaus, xarray, zarr
- meteorological data
- soil water capacity data

## ⚠️ limitations

- hard-coded observable names, e.g. "max_air_temp"
- stressor-yield depression relation needs to be provided

## 💸 funding

The implementation of ARIS-lite in Python, this repository, is funded by
the Austrian Research Promotion Agency (FFG, www.ffg.at) as part of
CropShift.

<a href="https://www.ffg.at/">
<img src="https://www.ffg.at/sites/default/files/allgemeine_downloads/Logos_2018/FFG_Logo_EN_RGB_1000px.png"
alt="Logo FFG" style="width:15rem;">
</a>

## 📖 citation

APA:

Haacker, J. (2026). *ARIS-lite: Agricultural Risk Information System model in
Python* (Version 0.3.0) [Computer software]. Zenodo.
https://doi.org/10.5281/zenodo.<RECORD_ID>

BibTeX:

```bibtex
@software{haacker_2026_aris_lite,
  author  = {Haacker, Jan},
  title   = {ARIS-lite: Agricultural Risk Information System model in Python},
  version = {0.3.0},
  year    = {2026},
  publisher = {Zenodo},
  doi     = {10.5281/zenodo.<RECORD_ID>},
  url     = {https://doi.org/10.5281/zenodo.<RECORD_ID>}
}
```

Replace `<RECORD_ID>` with the actual Zenodo record id after publication.

## 📚 references

1. Allen, R. G. (Ed.). (2000). Crop evapotranspiration: Guidelines
   for computing crop water requirements (repr). Food and
   Agriculture Organization of the United Nations.
2. Eitzinger, J., Daneu, V., Kubu, G., Thaler, S., Trnka, M.,
   Schaumberger, A., Schneider, S., & Tran, T. M. A. (2024). Grid based
   monitoring and forecasting system of cropping conditions and risks
   by agrometeorological indicators in Austria – Agricultural Risk
   Information System ARIS. Climate Services, 34, 1.
   <https://doi.org/10.1016/j.cliser.2024.100478>.
3. Schaumberger, A. (2011). Räumliche Modelle zur Vegetations- und
   Ertragsdynamik im Wirtschaftsgrünland [Dissertation, Graz University
   of Technology].
   <https://repository.tugraz.at/publications/npc97-y3058>.
