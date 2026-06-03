v {xschem version=3.4.7 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
C {devices/ipin.sym} -800 -700 0 0 {name=p_VDD lab=VDD}
C {devices/ipin.sym} -800 280 0 0 {name=p_VSS lab=VSS}
C {devices/ipin.sym} 200 -440 0 0 {name=p_Vinp lab=Vinp}
C {devices/ipin.sym} 1500 -440 0 1 {name=p_Vinn lab=Vinn}
C {devices/opin.sym} 1500 -320 0 0 {name=p_Voutp lab=Voutp}
N -800 -700 1400 -700 {lab=VDD}
N -800 280 1400 280 {lab=VSS}
C {sky130_fd_pr/pfet_01v8_lvt.sym} -500 -600 0 0 {name=MPR
W=10
L=1.0
nf=2
mult=1
ad="expr('int((@nf + 1)/2) * @W / @nf * 0.29')"
pd="expr('2*int((@nf + 1)/2) * (@W / @nf + 0.29)')"
as="expr('int((@nf + 2)/2) * @W / @nf * 0.29')"
ps="expr('2*int((@nf + 2)/2) * (@W / @nf + 0.29)')"
nrd="expr('0.29 / @W ')" nrs="expr('0.29 / @W ')"
sa=0 sb=0 sd=0
model=pfet_01v8_lvt
spiceprefix=X
}
N -480 -630 -480 -700 {lab=VDD}
N -520 -600 -550 -600 {lab=VP1}
N -550 -600 -550 -570 {lab=VP1}
N -550 -570 -480 -570 {lab=VP1}
C {devices/lab_pin.sym} -440 -570 0 0 {name=l_VP1 sig_type=std_logic lab=VP1}
C {sky130_fd_pr/pfet_01v8_lvt.sym} -500 -550 0 0 {name=MPC
W=10
L=1.0
nf=2
mult=1
ad="expr('int((@nf + 1)/2) * @W / @nf * 0.29')"
pd="expr('2*int((@nf + 1)/2) * (@W / @nf + 0.29)')"
as="expr('int((@nf + 2)/2) * @W / @nf * 0.29')"
ps="expr('2*int((@nf + 2)/2) * (@W / @nf + 0.29)')"
nrd="expr('0.29 / @W ')" nrs="expr('0.29 / @W ')"
sa=0 sb=0 sd=0
model=pfet_01v8_lvt
spiceprefix=X
}
N -480 -580 -480 -570 {lab=VP1}
N -520 -550 -570 -550 {lab=VP2}
N -570 -550 -570 -520 {lab=VP2}
N -570 -520 -480 -520 {lab=VP2}
C {devices/lab_pin.sym} -440 -520 0 0 {name=l_VP2 sig_type=std_logic lab=VP2}
C {devices/res.sym} -480 -310 0 0 {name=Rp value=20k footprint=1206 device=resistor m=1}
N -480 -520 -480 -340 {lab=VP2}
C {devices/isource.sym} -480 0 0 0 {name=I1 value=10u}
N -480 -280 -480 -30 {lab=n_rp_i1}
N -480 30 -480 280 {lab=VSS}
C {sky130_fd_pr/pfet_01v8_lvt.sym} -300 -600 0 0 {name=MP3
W=10
L=1.0
nf=2
mult=1
ad="expr('int((@nf + 1)/2) * @W / @nf * 0.29')"
pd="expr('2*int((@nf + 1)/2) * (@W / @nf + 0.29)')"
as="expr('int((@nf + 2)/2) * @W / @nf * 0.29')"
ps="expr('2*int((@nf + 2)/2) * (@W / @nf + 0.29)')"
nrd="expr('0.29 / @W ')" nrs="expr('0.29 / @W ')"
sa=0 sb=0 sd=0
model=pfet_01v8_lvt
spiceprefix=X
}
N -280 -630 -280 -700 {lab=VDD}
N -320 -600 -360 -600 {lab=VP1}
C {devices/lab_pin.sym} -380 -600 0 0 {name=l_VP1 sig_type=std_logic lab=VP1}
C {sky130_fd_pr/pfet_01v8_lvt.sym} -300 -550 0 0 {name=MP8
W=10
L=1.0
nf=2
mult=1
ad="expr('int((@nf + 1)/2) * @W / @nf * 0.29')"
pd="expr('2*int((@nf + 1)/2) * (@W / @nf + 0.29)')"
as="expr('int((@nf + 2)/2) * @W / @nf * 0.29')"
ps="expr('2*int((@nf + 2)/2) * (@W / @nf + 0.29)')"
nrd="expr('0.29 / @W ')" nrs="expr('0.29 / @W ')"
sa=0 sb=0 sd=0
model=pfet_01v8_lvt
spiceprefix=X
}
N -280 -580 -280 -570 {lab=n_mp3_mp8}
N -320 -550 -350 -550 {lab=n_mp8_d}
N -350 -550 -350 -520 {lab=n_mp8_d}
N -350 -520 -280 -520 {lab=n_mp8_d}
C {devices/res.sym} -280 -310 0 0 {name=Rp2 value=20k footprint=1206 device=resistor m=1}
N -280 -520 -280 -340 {lab=n_mp8_d}
C {sky130_fd_pr/nfet_01v8_lvt.sym} -300 -50 0 0 {name=MN9
W=4
L=0.5
nf=2
mult=1
ad="expr('int((@nf + 1)/2) * @W / @nf * 0.29')"
pd="expr('2*int((@nf + 1)/2) * (@W / @nf + 0.29)')"
as="expr('int((@nf + 2)/2) * @W / @nf * 0.29')"
ps="expr('2*int((@nf + 2)/2) * (@W / @nf + 0.29)')"
nrd="expr('0.29 / @W ')" nrs="expr('0.29 / @W ')"
sa=0 sb=0 sd=0
model=nfet_01v8_lvt
spiceprefix=X
}
N -280 -80 -280 -280 {lab=VN1}
N -320 -50 -350 -50 {lab=VN1}
N -350 -50 -350 -80 {lab=VN1}
N -350 -80 -280 -80 {lab=VN1}
C {devices/lab_pin.sym} -240 -80 0 0 {name=l_VN1 sig_type=std_logic lab=VN1}
C {sky130_fd_pr/nfet_01v8_lvt.sym} -300 250 0 0 {name=MN10
W=4
L=0.5
nf=2
mult=1
ad="expr('int((@nf + 1)/2) * @W / @nf * 0.29')"
pd="expr('2*int((@nf + 1)/2) * (@W / @nf + 0.29)')"
as="expr('int((@nf + 2)/2) * @W / @nf * 0.29')"
ps="expr('2*int((@nf + 2)/2) * (@W / @nf + 0.29)')"
nrd="expr('0.29 / @W ')" nrs="expr('0.29 / @W ')"
sa=0 sb=0 sd=0
model=nfet_01v8_lvt
spiceprefix=X
}
N -280 220 -280 -20 {lab=VN2}
N -280 280 -280 280 {lab=VSS}
N -320 250 -370 250 {lab=VN2}
N -370 250 -370 220 {lab=VN2}
N -370 220 -280 220 {lab=VN2}
C {devices/lab_pin.sym} -240 220 0 0 {name=l_VN2 sig_type=std_logic lab=VN2}
C {sky130_fd_pr/pfet_01v8_lvt.sym} 600 -600 0 0 {name=MTL
W=20
L=0.5
nf=4
mult=1
ad="expr('int((@nf + 1)/2) * @W / @nf * 0.29')"
pd="expr('2*int((@nf + 1)/2) * (@W / @nf + 0.29)')"
as="expr('int((@nf + 2)/2) * @W / @nf * 0.29')"
ps="expr('2*int((@nf + 2)/2) * (@W / @nf + 0.29)')"
nrd="expr('0.29 / @W ')" nrs="expr('0.29 / @W ')"
sa=0 sb=0 sd=0
model=pfet_01v8_lvt
spiceprefix=X
}
N 620 -630 620 -700 {lab=VDD}
N 580 -600 -150 -600 {lab=VP1}
N -150 -600 -150 -640 {lab=VP1}
N -150 -640 -180 -640 {lab=VP1}
C {devices/lab_pin.sym} 560 -600 0 0 {name=l_VP1 sig_type=std_logic lab=VP1}
N 620 -570 620 -480 {lab=Vtail}
C {devices/lab_pin.sym} 620 -490 0 0 {name=l_Vtail sig_type=std_logic lab=Vtail}
N 620 -480 520 -480 {lab=Vtail}
N 620 -480 680 -480 {lab=Vtail}
C {sky130_fd_pr/pfet_01v8_lvt.sym} 500 -440 0 0 {name=MP_L
W=20
L=0.5
nf=4
mult=1
ad="expr('int((@nf + 1)/2) * @W / @nf * 0.29')"
pd="expr('2*int((@nf + 1)/2) * (@W / @nf + 0.29)')"
as="expr('int((@nf + 2)/2) * @W / @nf * 0.29')"
ps="expr('2*int((@nf + 2)/2) * (@W / @nf + 0.29)')"
nrd="expr('0.29 / @W ')" nrs="expr('0.29 / @W ')"
sa=0 sb=0 sd=0
model=pfet_01v8_lvt
spiceprefix=X
}
N 520 -470 520 -480 {lab=Vtail}
N 480 -440 220 -440 {lab=Vinp}
C {devices/lab_pin.sym} 460 -440 0 0 {name=l_Vinp sig_type=std_logic lab=Vinp}
N 520 -410 520 -200 {lab=Vmidn}
C {devices/lab_pin.sym} 520 -210 0 0 {name=l_Vmidn sig_type=std_logic lab=Vmidn}
C {sky130_fd_pr/pfet_01v8_lvt.sym} 700 -440 0 1 {name=MP_R
W=20
L=0.5
nf=4
mult=1
ad="expr('int((@nf + 1)/2) * @W / @nf * 0.29')"
pd="expr('2*int((@nf + 1)/2) * (@W / @nf + 0.29)')"
as="expr('int((@nf + 2)/2) * @W / @nf * 0.29')"
ps="expr('2*int((@nf + 2)/2) * (@W / @nf + 0.29)')"
nrd="expr('0.29 / @W ')" nrs="expr('0.29 / @W ')"
sa=0 sb=0 sd=0
model=pfet_01v8_lvt
spiceprefix=X
}
N 680 -470 680 -480 {lab=Vtail}
N 720 -440 1480 -440 {lab=Vinn}
C {devices/lab_pin.sym} 740 -440 0 0 {name=l_Vinn sig_type=std_logic lab=Vinn}
N 680 -410 680 -200 {lab=Vmidp}
C {devices/lab_pin.sym} 680 -210 0 0 {name=l_Vmidp sig_type=std_logic lab=Vmidp}
C {sky130_fd_pr/nfet_01v8_lvt.sym} 500 250 0 0 {name=MNF_L
W=8
L=0.5
nf=4
mult=1
ad="expr('int((@nf + 1)/2) * @W / @nf * 0.29')"
pd="expr('2*int((@nf + 1)/2) * (@W / @nf + 0.29)')"
as="expr('int((@nf + 2)/2) * @W / @nf * 0.29')"
ps="expr('2*int((@nf + 2)/2) * (@W / @nf + 0.29)')"
nrd="expr('0.29 / @W ')" nrs="expr('0.29 / @W ')"
sa=0 sb=0 sd=0
model=nfet_01v8_lvt
spiceprefix=X
}
N 520 220 520 -200 {lab=Vmidn}
N 520 280 520 280 {lab=VSS}
N 480 250 -120 250 {lab=VN1}
N -120 250 -120 -200 {lab=VN1}
N -120 -200 -180 -200 {lab=VN1}
C {devices/lab_pin.sym} 460 250 0 0 {name=l_VN1 sig_type=std_logic lab=VN1}
C {sky130_fd_pr/nfet_01v8_lvt.sym} 700 250 0 1 {name=MNF_R
W=8
L=0.5
nf=4
mult=1
ad="expr('int((@nf + 1)/2) * @W / @nf * 0.29')"
pd="expr('2*int((@nf + 1)/2) * (@W / @nf + 0.29)')"
as="expr('int((@nf + 2)/2) * @W / @nf * 0.29')"
ps="expr('2*int((@nf + 2)/2) * (@W / @nf + 0.29)')"
nrd="expr('0.29 / @W ')" nrs="expr('0.29 / @W ')"
sa=0 sb=0 sd=0
model=nfet_01v8_lvt
spiceprefix=X
}
N 680 220 680 -200 {lab=Vmidp}
N 680 280 680 280 {lab=VSS}
N 720 250 770 250 {lab=VN1}
C {devices/lab_pin.sym} 740 250 0 0 {name=l_VN1 sig_type=std_logic lab=VN1}
C {sky130_fd_pr/pfet_01v8_lvt.sym} 1000 -550 0 0 {name=ML_D
W=20
L=0.5
nf=4
mult=1
ad="expr('int((@nf + 1)/2) * @W / @nf * 0.29')"
pd="expr('2*int((@nf + 1)/2) * (@W / @nf + 0.29)')"
as="expr('int((@nf + 2)/2) * @W / @nf * 0.29')"
ps="expr('2*int((@nf + 2)/2) * (@W / @nf + 0.29)')"
nrd="expr('0.29 / @W ')" nrs="expr('0.29 / @W ')"
sa=0 sb=0 sd=0
model=pfet_01v8_lvt
spiceprefix=X
}
N 1020 -580 1020 -700 {lab=VDD}
N 980 -550 930 -550 {lab=VP1}
C {devices/lab_pin.sym} 960 -550 0 0 {name=l_VP1 sig_type=std_logic lab=VP1}
C {sky130_fd_pr/pfet_01v8_lvt.sym} 1000 -350 0 0 {name=MC_D
W=20
L=0.5
nf=4
mult=1
ad="expr('int((@nf + 1)/2) * @W / @nf * 0.29')"
pd="expr('2*int((@nf + 1)/2) * (@W / @nf + 0.29)')"
as="expr('int((@nf + 2)/2) * @W / @nf * 0.29')"
ps="expr('2*int((@nf + 2)/2) * (@W / @nf + 0.29)')"
nrd="expr('0.29 / @W ')" nrs="expr('0.29 / @W ')"
sa=0 sb=0 sd=0
model=pfet_01v8_lvt
spiceprefix=X
}
N 1020 -380 1020 -520 {lab=n_ml_d_drain}
N 980 -350 930 -350 {lab=VP2}
C {devices/lab_pin.sym} 960 -350 0 0 {name=l_VP2 sig_type=std_logic lab=VP2}
C {devices/lab_pin.sym} 1020 -330 0 0 {name=l_A sig_type=std_logic lab=A}
C {sky130_fd_pr/nfet_01v8_lvt.sym} 1000 -50 0 0 {name=MNC_D
W=8
L=0.5
nf=4
mult=1
ad="expr('int((@nf + 1)/2) * @W / @nf * 0.29')"
pd="expr('2*int((@nf + 1)/2) * (@W / @nf + 0.29)')"
as="expr('int((@nf + 2)/2) * @W / @nf * 0.29')"
ps="expr('2*int((@nf + 2)/2) * (@W / @nf + 0.29)')"
nrd="expr('0.29 / @W ')" nrs="expr('0.29 / @W ')"
sa=0 sb=0 sd=0
model=nfet_01v8_lvt
spiceprefix=X
}
N 1020 -80 1020 -320 {lab=A}
N 980 -50 930 -50 {lab=VN2}
C {devices/lab_pin.sym} 960 -50 0 0 {name=l_VN2 sig_type=std_logic lab=VN2}
C {sky130_fd_pr/nfet_01v8_lvt.sym} 1000 250 0 0 {name=MN1
W=8
L=0.5
nf=4
mult=1
ad="expr('int((@nf + 1)/2) * @W / @nf * 0.29')"
pd="expr('2*int((@nf + 1)/2) * (@W / @nf + 0.29)')"
as="expr('int((@nf + 2)/2) * @W / @nf * 0.29')"
ps="expr('2*int((@nf + 2)/2) * (@W / @nf + 0.29)')"
nrd="expr('0.29 / @W ')" nrs="expr('0.29 / @W ')"
sa=0 sb=0 sd=0
model=nfet_01v8_lvt
spiceprefix=X
}
N 1020 220 1020 -20 {lab=Vfold_L}
N 1020 280 1020 280 {lab=VSS}
N 980 250 950 250 {lab=mirror_gate}
N 950 250 950 220 {lab=mirror_gate}
N 950 220 1020 220 {lab=mirror_gate}
N 520 -200 1020 -200 {lab=Vmidn}
N 1020 -200 1020 220 {lab=Vmidn}
C {sky130_fd_pr/pfet_01v8_lvt.sym} 1200 -550 0 1 {name=ML_O
W=20
L=0.5
nf=4
mult=1
ad="expr('int((@nf + 1)/2) * @W / @nf * 0.29')"
pd="expr('2*int((@nf + 1)/2) * (@W / @nf + 0.29)')"
as="expr('int((@nf + 2)/2) * @W / @nf * 0.29')"
ps="expr('2*int((@nf + 2)/2) * (@W / @nf + 0.29)')"
nrd="expr('0.29 / @W ')" nrs="expr('0.29 / @W ')"
sa=0 sb=0 sd=0
model=pfet_01v8_lvt
spiceprefix=X
}
N 1180 -580 1180 -700 {lab=VDD}
N 1220 -550 1270 -550 {lab=VP1}
C {devices/lab_pin.sym} 1240 -550 0 0 {name=l_VP1 sig_type=std_logic lab=VP1}
C {sky130_fd_pr/pfet_01v8_lvt.sym} 1200 -350 0 1 {name=MC_O
W=20
L=0.5
nf=4
mult=1
ad="expr('int((@nf + 1)/2) * @W / @nf * 0.29')"
pd="expr('2*int((@nf + 1)/2) * (@W / @nf + 0.29)')"
as="expr('int((@nf + 2)/2) * @W / @nf * 0.29')"
ps="expr('2*int((@nf + 2)/2) * (@W / @nf + 0.29)')"
nrd="expr('0.29 / @W ')" nrs="expr('0.29 / @W ')"
sa=0 sb=0 sd=0
model=pfet_01v8_lvt
spiceprefix=X
}
N 1180 -380 1180 -520 {lab=n_ml_o_drain}
N 1220 -350 1270 -350 {lab=VP2}
C {devices/lab_pin.sym} 1240 -350 0 0 {name=l_VP2 sig_type=std_logic lab=VP2}
C {devices/lab_pin.sym} 1190 -330 0 0 {name=l_Voutp sig_type=std_logic lab=Voutp}
C {sky130_fd_pr/nfet_01v8_lvt.sym} 1200 -50 0 1 {name=MNC_O
W=8
L=0.5
nf=4
mult=1
ad="expr('int((@nf + 1)/2) * @W / @nf * 0.29')"
pd="expr('2*int((@nf + 1)/2) * (@W / @nf + 0.29)')"
as="expr('int((@nf + 2)/2) * @W / @nf * 0.29')"
ps="expr('2*int((@nf + 2)/2) * (@W / @nf + 0.29)')"
nrd="expr('0.29 / @W ')" nrs="expr('0.29 / @W ')"
sa=0 sb=0 sd=0
model=nfet_01v8_lvt
spiceprefix=X
}
N 1180 -80 1180 -320 {lab=Voutp}
N 1220 -50 1270 -50 {lab=VN2}
C {devices/lab_pin.sym} 1240 -50 0 0 {name=l_VN2 sig_type=std_logic lab=VN2}
C {sky130_fd_pr/nfet_01v8_lvt.sym} 1200 250 0 1 {name=MN2
W=8
L=0.5
nf=4
mult=1
ad="expr('int((@nf + 1)/2) * @W / @nf * 0.29')"
pd="expr('2*int((@nf + 1)/2) * (@W / @nf + 0.29)')"
as="expr('int((@nf + 2)/2) * @W / @nf * 0.29')"
ps="expr('2*int((@nf + 2)/2) * (@W / @nf + 0.29)')"
nrd="expr('0.29 / @W ')" nrs="expr('0.29 / @W ')"
sa=0 sb=0 sd=0
model=nfet_01v8_lvt
spiceprefix=X
}
N 1180 220 1180 -20 {lab=Vfold_R}
N 1180 280 1180 280 {lab=VSS}
N 950 250 950 330 {lab=mirror_gate}
N 950 330 1250 330 {lab=mirror_gate}
N 1250 330 1250 250 {lab=mirror_gate}
N 1250 250 1220 250 {lab=mirror_gate}
N 680 -200 1180 -200 {lab=Vmidp}
N 1180 -200 1180 220 {lab=Vmidp}
C {devices/capa.sym} 1400 -200 0 0 {name=CL value=1p footprint=1206 device="ceramic capacitor"}
N 1400 -230 1180 -320 {lab=Voutp}
N 1400 -170 1400 280 {lab=VSS}
