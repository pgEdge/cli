
pgmlV=2.9.3.2
pgMajorV=16
pgMinorV=4
pgV=$pgMajorV.$pgMinorV
pgmlXX=pgml-pg$pgMajorV
cargoV=0.11.3

plat=arm
if [ `arch` == "x86_64" ]; then
  plat="amd"
fi


