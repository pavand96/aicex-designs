v {xschem version=3.4.7 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
N 470 -210 590 -210 {lab=VSS}
N 610 -300 610 -210 {lab=VSS}
N 590 -210 610 -210 {lab=VSS}
N 610 -330 660 -330 {lab=VSS}
N 660 -330 660 -270 {lab=VSS}
N 610 -270 660 -270 {lab=VSS}
N 440 -330 560 -330 {lab=VIN}
N 560 -330 570 -330 {lab=VIN}
N 610 -410 610 -360 {lab=VOUT}
N 550 -650 610 -650 {lab=VDD}
N 610 -650 610 -610 {lab=VDD}
N 610 -380 750 -380 {lab=VOUT}
N 610 -440 610 -410 {lab=VOUT}
N 610 -550 610 -500 {lab=#net1}
C {cborder/border_xs.sym} 0 0 0 0 {
user="wulff"
company="wulff"}
C {devices/opin.sym} 750 -380 0 0 {name=p1 lab=VOUT}
C {devices/ipin.sym} 470 -210 0 0 {name=p2 lab=VSS}
C {sky130_fd_pr/nfet_01v8.sym} 590 -330 0 0 {name=M2
W=40.0
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
C {devices/ipin.sym} 550 -650 0 0 {name=p3 lab=VDD}
C {devices/ipin.sym} 440 -330 0 0 {name=p4 lab=VIN}
C {devices/vsource.sym} 610 -470 0 0 {name=V1 value=0 savecurrent=true}
C {devices/res.sym} 610 -580 0 0 {name=R1
value=50k
footprint=1206
device=resistor
m=1}
