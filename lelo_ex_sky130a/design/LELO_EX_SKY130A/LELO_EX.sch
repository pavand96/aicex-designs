v {xschem version=3.4.7 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
N 450 -370 450 -290 {lab=#net1}
N 690 -370 690 -290 {lab=#net2}
N 120 -170 240 -170 {lab=VSS}
N 740 -400 740 -350 {lab=VSS}
N 700 -400 740 -400 {lab=VSS}
N 690 -400 700 -400 {lab=VSS}
N 400 -400 450 -400 {lab=VSS}
N 400 -400 400 -360 {lab=VSS}
N 400 -360 400 -340 {lab=VSS}
N 450 -530 450 -430 {lab=IBPS_5U}
N 370 -530 450 -530 {lab=IBPS_5U}
N 490 -400 640 -400 {lab=IBPS_5U}
N 540 -460 540 -400 {lab=IBPS_5U}
N 450 -460 540 -460 {lab=IBPS_5U}
N 690 -520 690 -430 {lab=IBPS_20U}
N 690 -520 830 -520 {lab=IBPS_20U}
N 880 -370 880 -310 {lab=#net3}
N 880 -440 880 -430 {lab=IBPS_20U}
N 880 -470 880 -440 {lab=IBPS_20U}
N 690 -470 870 -470 {lab=IBPS_20U}
N 870 -470 880 -470 {lab=IBPS_20U}
N 880 -400 930 -400 {lab=VSS}
N 930 -400 930 -340 {lab=VSS}
N 800 -400 840 -400 {lab=IBPS_5U}
N 540 -440 800 -440 {lab=IBPS_5U}
N 630 -400 650 -400 {lab=IBPS_5U}
N 800 -440 800 -400 {lab=IBPS_5U}
N 450 -230 450 -170 {lab=VSS}
N 240 -170 450 -170 {lab=VSS}
N 400 -260 400 -170 {lab=VSS}
N 400 -260 450 -260 {lab=VSS}
N 260 -340 400 -340 {lab=VSS}
N 260 -340 260 -170 {lab=VSS}
N 490 -260 550 -260 {lab=#net1}
N 550 -320 550 -260 {lab=#net1}
N 450 -320 550 -320 {lab=#net1}
N 550 -260 650 -260 {lab=#net1}
N 690 -230 690 -170 {lab=VSS}
N 450 -170 690 -170 {lab=VSS}
N 550 -310 810 -310 {lab=#net1}
N 810 -310 810 -260 {lab=#net1}
N 810 -260 840 -260 {lab=#net1}
N 880 -310 880 -290 {lab=#net3}
N 880 -230 880 -170 {lab=VSS}
N 690 -170 880 -170 {lab=VSS}
N 880 -260 930 -260 {lab=VSS}
N 930 -260 930 -210 {lab=VSS}
N 880 -210 930 -210 {lab=VSS}
N 690 -200 740 -200 {lab=VSS}
N 740 -260 740 -200 {lab=VSS}
N 690 -260 740 -260 {lab=VSS}
N 930 -340 930 -260 {lab=VSS}
N 740 -350 740 -260 {lab=VSS}
C {cborder/border_xs.sym} 0 0 0 0 {
user="wulff"
company="wulff"}
C {devices/ipin.sym} 370 -530 0 0 {name=p1 lab=IBPS_5U}
C {devices/ipin.sym} 120 -170 0 0 {name=p2 lab=VSS}
C {devices/ipin.sym} 830 -520 0 1 {name=p3 lab=IBPS_20U}
C {sky130_fd_pr/nfet_01v8.sym} 470 -260 0 1 {name=M1
W=30.0
L=0.8
nf=2 
mult=10
ad="expr('int((@nf + 1)/2) * @W / @nf * 0.29')"
pd="expr('2*int((@nf + 1)/2) * (@W / @nf + 0.29)')"
as="expr('int((@nf + 2)/2) * @W / @nf * 0.29')"
ps="expr('2*int((@nf + 2)/2) * (@W / @nf + 0.29)')"
nrd="expr('0.29 / @W ')" nrs="expr('0.29 / @W ')"
sa=0 sb=0 sd=0
model=nfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/nfet_01v8.sym} 670 -400 0 0 {name=M2
W=60.0
L=0.8
nf=2
mult=10
ad="expr('int((@nf + 1)/2) * @W / @nf * 0.29')"
pd="expr('2*int((@nf + 1)/2) * (@W / @nf + 0.29)')"
as="expr('int((@nf + 2)/2) * @W / @nf * 0.29')"
ps="expr('2*int((@nf + 2)/2) * (@W / @nf + 0.29)')"
nrd="expr('0.29 / @W ')" nrs="expr('0.29 / @W ')"
sa=0 sb=0 sd=0
model=nfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/nfet_01v8.sym} 470 -400 0 1 {name=M3
W=30.0
L=0.8
nf=2
mult=10
ad="expr('int((@nf + 1)/2) * @W / @nf * 0.29')"
pd="expr('2*int((@nf + 1)/2) * (@W / @nf + 0.29)')"
as="expr('int((@nf + 2)/2) * @W / @nf * 0.29')"
ps="expr('2*int((@nf + 2)/2) * (@W / @nf + 0.29)')"
nrd="expr('0.29 / @W ')" nrs="expr('0.29 / @W ')"
sa=0 sb=0 sd=0
model=nfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/nfet_01v8.sym} 860 -400 0 0 {name=M4
W=60.0
L=0.8
nf=2
mult=10
ad="expr('int((@nf + 1)/2) * @W / @nf * 0.29')"
pd="expr('2*int((@nf + 1)/2) * (@W / @nf + 0.29)')"
as="expr('int((@nf + 2)/2) * @W / @nf * 0.29')"
ps="expr('2*int((@nf + 2)/2) * (@W / @nf + 0.29)')"
nrd="expr('0.29 / @W ')" nrs="expr('0.29 / @W ')"
sa=0 sb=0 sd=0
model=nfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/nfet_01v8.sym} 670 -260 0 0 {name=M5
W=60.0
L=0.8
nf=2 
mult=10
ad="expr('int((@nf + 1)/2) * @W / @nf * 0.29')"
pd="expr('2*int((@nf + 1)/2) * (@W / @nf + 0.29)')"
as="expr('int((@nf + 2)/2) * @W / @nf * 0.29')"
ps="expr('2*int((@nf + 2)/2) * (@W / @nf + 0.29)')"
nrd="expr('0.29 / @W ')" nrs="expr('0.29 / @W ')"
sa=0 sb=0 sd=0
model=nfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/nfet_01v8.sym} 860 -260 0 0 {name=M6
W=60.0
L=0.8
nf=2
mult=10
ad="expr('int((@nf + 1)/2) * @W / @nf * 0.29')"
pd="expr('2*int((@nf + 1)/2) * (@W / @nf + 0.29)')"
as="expr('int((@nf + 2)/2) * @W / @nf * 0.29')"
ps="expr('2*int((@nf + 2)/2) * (@W / @nf + 0.29)')"
nrd="expr('0.29 / @W ')" nrs="expr('0.29 / @W ')"
sa=0 sb=0 sd=0
model=nfet_01v8
spiceprefix=X
}
