v {xschem version=3.4.7 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
N 650 -280 650 -240 {lab=#net1}
N 540 -330 540 -320 {lab=#net1}
N 540 -280 650 -280 {lab=#net1}
N 540 -320 540 -280 {lab=#net1}
N 650 -280 760 -280 {lab=#net1}
N 760 -330 760 -280 {lab=#net1}
N 540 -480 540 -390 {lab=#net2}
N 760 -480 760 -390 {lab=VOUT}
N 580 -510 720 -510 {lab=#net2}
N 630 -510 630 -450 {lab=#net2}
N 540 -450 630 -450 {lab=#net2}
N 540 -580 540 -540 {lab=VDD}
N 540 -580 760 -580 {lab=VDD}
N 760 -580 760 -540 {lab=VDD}
N 670 -620 670 -580 {lab=VDD}
N 650 -620 670 -620 {lab=VDD}
N 620 -120 650 -120 {lab=VSS}
N 650 -180 650 -120 {lab=VSS}
N 360 -210 610 -210 {lab=IBIAS}
N 320 -180 320 -150 {lab=VSS}
N 320 -150 650 -150 {lab=VSS}
N 320 -310 320 -240 {lab=IBIAS}
N 320 -360 320 -310 {lab=IBIAS}
N 300 -360 320 -360 {lab=IBIAS}
N 460 -360 500 -360 {lab=VINP}
N 800 -360 860 -360 {lab=VINN}
N 540 -360 600 -360 {lab=VSS}
N 700 -360 760 -360 {lab=VSS}
N 650 -210 690 -210 {lab=VSS}
N 690 -210 690 -150 {lab=VSS}
N 650 -150 690 -150 {lab=VSS}
N 470 -510 540 -510 {lab=VDD}
N 470 -580 470 -510 {lab=VDD}
N 470 -580 540 -580 {lab=VDD}
N 760 -510 830 -510 {lab=VDD}
N 830 -580 830 -510 {lab=VDD}
N 760 -580 830 -580 {lab=VDD}
N 320 -260 420 -260 {lab=IBIAS}
N 420 -260 420 -210 {lab=IBIAS}
N 720 -440 760 -440 {lab=VOUT}
N 600 -360 700 -360 {lab=VSS}
N 600 -360 600 -150 {lab=VSS}
N 270 -210 320 -210 {lab=VSS}
N 270 -210 270 -150 {lab=VSS}
N 270 -150 320 -150 {lab=VSS}
C {cborder/border_xs.sym} 0 0 0 0 {
user="wulff"
company="wulff"}
C {devices/ipin.sym} 650 -620 0 0 {name=p1 lab=VDD}
C {devices/ipin.sym} 620 -120 0 0 {name=p2 lab=VSS}
C {sky130_fd_pr/nfet_01v8.sym} 780 -360 0 1 {name=M2
W=80.0
L=0.8
nf=1 
mult=1
ad="expr('int((@nf + 1)/2) * @W / @nf * 0.29')"
pd="expr('2*int((@nf + 1)/2) * (@W / @nf + 0.29)')"
as="expr('int((@nf + 2)/2) * @W / @nf * 0.29')"
ps="expr('2*int((@nf + 2)/2) * (@W / @nf + 0.29)')"
nrd="expr('0.29 / @W ')" nrs="expr('0.29 / @W ')"
sa=0 sb=0 sd=0
model=nfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/pfet_01v8.sym} 740 -510 0 0 {name=M4
W=36.0
L=0.8
nf=1
mult=1
ad="expr('int((@nf + 1)/2) * @W / @nf * 0.29')"
pd="expr('2*int((@nf + 1)/2) * (@W / @nf + 0.29)')"
as="expr('int((@nf + 2)/2) * @W / @nf * 0.29')"
ps="expr('2*int((@nf + 2)/2) * (@W / @nf + 0.29)')"
nrd="expr('0.29 / @W ')" nrs="expr('0.29 / @W ')"
sa=0 sb=0 sd=0
model=pfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/pfet_01v8.sym} 560 -510 0 1 {name=M3
W=36.0
L=0.8
nf=1
mult=1
ad="expr('int((@nf + 1)/2) * @W / @nf * 0.29')"
pd="expr('2*int((@nf + 1)/2) * (@W / @nf + 0.29)')"
as="expr('int((@nf + 2)/2) * @W / @nf * 0.29')"
ps="expr('2*int((@nf + 2)/2) * (@W / @nf + 0.29)')"
nrd="expr('0.29 / @W ')" nrs="expr('0.29 / @W ')"
sa=0 sb=0 sd=0
model=pfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/nfet_01v8.sym} 340 -210 0 1 {name=M6
W=36
L=1.0
nf=1 
mult=1
ad="expr('int((@nf + 1)/2) * @W / @nf * 0.29')"
pd="expr('2*int((@nf + 1)/2) * (@W / @nf + 0.29)')"
as="expr('int((@nf + 2)/2) * @W / @nf * 0.29')"
ps="expr('2*int((@nf + 2)/2) * (@W / @nf + 0.29)')"
nrd="expr('0.29 / @W ')" nrs="expr('0.29 / @W ')"
sa=0 sb=0 sd=0
model=nfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/nfet_01v8.sym} 520 -360 0 0 {name=M1
W=80
L=0.8
nf=1 
mult=1
ad="expr('int((@nf + 1)/2) * @W / @nf * 0.29')"
pd="expr('2*int((@nf + 1)/2) * (@W / @nf + 0.29)')"
as="expr('int((@nf + 2)/2) * @W / @nf * 0.29')"
ps="expr('2*int((@nf + 2)/2) * (@W / @nf + 0.29)')"
nrd="expr('0.29 / @W ')" nrs="expr('0.29 / @W ')"
sa=0 sb=0 sd=0
model=nfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/nfet_01v8.sym} 630 -210 0 0 {name=M5
W=36.0
L=1.0
nf=1 
mult=1
ad="expr('int((@nf + 1)/2) * @W / @nf * 0.29')"
pd="expr('2*int((@nf + 1)/2) * (@W / @nf + 0.29)')"
as="expr('int((@nf + 2)/2) * @W / @nf * 0.29')"
ps="expr('2*int((@nf + 2)/2) * (@W / @nf + 0.29)')"
nrd="expr('0.29 / @W ')" nrs="expr('0.29 / @W ')"
sa=0 sb=0 sd=0
model=nfet_01v8
spiceprefix=X
}
C {devices/opin.sym} 720 -440 0 1 {name=p3 lab=VOUT}
C {devices/ipin.sym} 300 -360 0 0 {name=p4 lab=IBIAS}
C {devices/ipin.sym} 460 -360 0 0 {name=p6 lab=VINP}
C {devices/ipin.sym} 860 -360 0 1 {name=p8 lab=VINN}
