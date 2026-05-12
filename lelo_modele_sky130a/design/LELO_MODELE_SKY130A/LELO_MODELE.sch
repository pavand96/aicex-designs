v {xschem version=3.4.7 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
N 470 -210 590 -210 {lab=VS}
N 610 -300 610 -210 {lab=VS}
N 590 -210 610 -210 {lab=VS}
N 610 -330 660 -330 {lab=VB}
N 660 -330 660 -270 {lab=VB}
N 610 -270 660 -270 {lab=VB}
N 440 -330 560 -330 {lab=VG}
N 560 -330 570 -330 {lab=VG}
N 610 -410 610 -360 {lab=VD}
N 610 -480 610 -440 {lab=VD}
N 610 -380 750 -380 {lab=VD}
N 610 -440 610 -410 {lab=VD}
C {cborder/border_xs.sym} 0 0 0 0 {
user="wulff"
company="wulff"}
C {devices/ipin.sym} 750 -380 0 0 {name=p1 lab=VD}
C {devices/ipin.sym} 470 -210 0 0 {name=p2 lab=VS}
C {sky130_fd_pr/nfet_01v8.sym} 590 -330 0 0 {name=M2
W=51.00
L=0.8000
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
C {devices/ipin.sym} 440 -330 0 0 {name=p4 lab=VG}
N 440 -270 610 -270 {lab=VB}
C {devices/ipin.sym} 440 -270 0 0 {name=p3 lab=VB}
