v {xschem version=3.4.7 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
N 550 -400 550 -330 {lab=VD}
N 370 -430 510 -430 {lab=VG}
N 550 -520 550 -460 {lab=VDD}
N 450 -520 480 -520 {lab=VDD}
N 480 -520 550 -520 {lab=VDD}
N 550 -430 620 -430 {lab=VD}
N 490 -330 550 -330 {lab=VD}
N 620 -430 680 -430 {lab=VD}
C {cborder/border_xs.sym} 0 0 0 0 {
user="wulff"
company="wulff"}
C {devices/ipin.sym} 450 -520 0 0 {name=p1 lab=VDD}
C {devices/ipin.sym} 370 -430 0 0 {name=p3 lab=VG}
C {devices/ipin.sym} 680 -430 0 1 {name=p6 lab=VB}
C {sky130_fd_pr/pfet_01v8.sym} 530 -430 0 0 {name=M2
W=80.00
L=0.8000
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
C {devices/ipin.sym} 490 -330 0 0 {name=p2 lab=VD}
