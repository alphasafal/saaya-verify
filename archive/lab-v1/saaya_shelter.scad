// SAAYA VERIFY - editable miniature concept, millimetres.
// Open with OpenSCAD. F5 preview; F6 render. Set part_to_export for STL.
// Not a fabrication-validated assembly. External components are envelopes.
part_to_export = "assembly"; // assembly, structure, upper_roof, lower_roof
exploded = true;
show_optional = true;
base_x=250; base_y=200; base_t=5;
pillar_h=160; pillar_t=10;
roof_x=270; roof_y=220; roof_t=3; roof_gap=12;
roof_z=base_t+pillar_h;
module block(p,s,c) { color(c) translate(p) cube(s); }
module structure(){
 block([0,0,0],[base_x,base_y,base_t],"silver");
 for(x=[8,base_x-18],y=[8,base_y-18]) block([x,y,base_t],[pillar_t,pillar_t,pillar_h],"teal");
 block([20,137,43],[120,45,5],"tan");
 for(x=[27,124]) block([x,145,5],[8,30,38],"sienna");
}
module roof(){cube([roof_x,roof_y,roof_t]);}
module components(){
 block([145,40,5],[100,70,35],"darkslategray");
 block([154,38,20],[30,2,15],"lightgreen");
 for(x=[193,209,225]) block([x,37,23],[9,3,9],x==209?"tomato":"gold");
 block([235,37,33],[5,3,5],"orange");
 block([20,35,5],[38,42,53],"skyblue");
 block([28,45,50],[8,10,10],"gold");
 block([-22,57,89],[14,18,16],"gold");
 block([-15,65,83],[28,4,4],"teal");
 block([10,115,68],[10,12,12],"gold");
 block([12,119,5],[4,4,63],"teal");
 // Fan envelope, with intake opening. Grille detail conceptual only.
 color("slategray") translate([178,164,108]) difference(){cube([44,10,44]);translate([22,-1,22]) rotate([-90,0,0]) cylinder(h=12,r=18,$fn=40);}
 block([215,173,108],[22,5,5],"teal");
 if(show_optional) block([165,122,5],[70,32,30],"tan");
}
if(part_to_export=="upper_roof" || part_to_export=="lower_roof") roof();
else if(part_to_export=="structure") structure();
else {
 structure();components();
 color("lightgray") translate([-10,-10,roof_z+(exploded?25:0)]) roof();
 color("white") translate([-10,-10,roof_z+roof_t+roof_gap+(exploded?65:0)]) roof();
 if(show_optional){
 block([40,30,roof_z+roof_t+roof_gap+5+(exploded?65:0)],[130,85,4],"steelblue");
 block([225,180,roof_z+roof_t+roof_gap+4+(exploded?65:0)],[12,12,3],"gold");
 block([18,50,roof_z+3+(exploded?25:0)],[10,10,3],"gold");
 }
}
