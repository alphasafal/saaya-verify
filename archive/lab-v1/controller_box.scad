// SAAYA dry electronics enclosure: external assembly 100 x 70 x 35 mm.
// Nominal holes and boards; measure actual components before fabrication.
// part_to_export: assembly, base, lid. F6 then File > Export > STL.
part_to_export="assembly";
exploded=true; show_boards=true;
L=100; W=70; H=35; wall=2.5; lid_t=2.5;
$fn=40;
module shell(){
 difference(){
  cube([L,W,H-lid_t]);
  translate([wall,wall,wall]) cube([L-2*wall,W-2*wall,H]);
  // Front display aperture: fit to chosen module.
  translate([9,-1,13]) cube([30,wall+2,15]);
  for(x=[52,68,84]) translate([x,-1,17]) rotate([-90,0,0]) cylinder(h=wall+2,d=7);
  translate([94,-1,25]) rotate([-90,0,0]) cylinder(h=wall+2,d=3);
  // Rear glands: sensor wiring and separate power/fan wiring.
  for(x=[18,76]) translate([x,W-wall-1,12]) rotate([-90,0,0]) cylinder(h=wall+2,d=7);
 }
 // Lid screw bosses, not threads. Use appropriate inserts/fasteners.
 for(x=[5,L-5],y=[5,W-5]) translate([x,y,wall]) difference(){cylinder(h=H-lid_t-wall,d=7);translate([0,0,-1]) cylinder(h=H,d=2.5);}
}
module lid(){difference(){cube([L,W,lid_t]);for(x=[5,L-5],y=[5,W-5])translate([x,y,-1])cylinder(h=lid_t+2,d=3);}}
module board(p,s,c){color(c)translate(p)cube(s);}
if(part_to_export=="base")shell();
else if(part_to_export=="lid")lid();
else {
 color("slategray")shell();
 color("lightgray")translate([0,0,H-lid_t+(exploded?28:0)])lid();
 if(show_boards){
  board([8,30,6],[52,25,5],"seagreen"); // ESP32 nominal
  board([65,40,6],[27,19,6],"indianred"); // fan driver
  board([65,15,6],[27,18,6],"goldenrod"); // buck
  board([8,8,6],[27,16,4],"teal"); // optional INA219
  board([38,8,6],[22,16,4],"peru"); // I/O terminals
 }
}
