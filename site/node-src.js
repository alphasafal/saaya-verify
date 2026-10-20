import * as THREE from 'three';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';
import {STLLoader} from 'three/addons/loaders/STLLoader.js';
// SAAYA Node v1 viewer. Views: #assembly, #internals, #front, #bottom. ?shot=1 hides UI for renders.
const host = document.querySelector('#node-canvas'), info = document.querySelector('#node-info');
const shot = new URLSearchParams(location.search).has('shot');
const data = await fetch('node/node.json', {cache: 'no-cache'}).then(r => r.json());
const scene = new THREE.Scene(); scene.background = new THREE.Color(shot ? '#ffffff' : '#eef1e8');
const camera = new THREE.PerspectiveCamera(30, 1, 1, 10000); camera.up.set(0, 0, 1);
const renderer = new THREE.WebGLRenderer({antialias: true, preserveDrawingBuffer: true});
renderer.setPixelRatio(Math.min(devicePixelRatio, 2)); host.append(renderer.domElement);
const orbit = new OrbitControls(camera, renderer.domElement); orbit.enableDamping = !shot;
scene.add(new THREE.HemisphereLight('#ffffff', '#8a9a88', 2.2));
const sun = new THREE.DirectionalLight('#ffffff', 2.4); sun.position.set(-300, -600, 800); scene.add(sun);
const loader = new STLLoader(), meshes = {};
await Promise.all(data.parts.map(async p => {
  const g = await loader.loadAsync('node/' + p.name + '.stl'); g.computeVertexNormals();
  const m = new THREE.Mesh(g, new THREE.MeshStandardMaterial({color: p.color, roughness: .55, metalness: p.group === 'mounting' ? .4 : .05, side: THREE.DoubleSide}));
  const e = new THREE.LineSegments(new THREE.EdgesGeometry(g, 30), new THREE.LineBasicMaterial({color: '#4a4f4a', transparent: true, opacity: .35}));
  m.add(e); m.userData = p; scene.add(m); meshes[p.name] = m;
}));
const views = {
  assembly: {pos: [-430, -560, 330], target: [40, 35, 50], hide: []},
  internals: {pos: [-110, -320, 250], target: [88, 45, 50], hide: ['enclosure_lid', 'oled_glass', 'help_button', 'mode_button', 'status_led', 'buzzer', 'oled_module', 'radiation_shield', 'sht31_in_shield', 'fan_120', 'fan_guard']},
  front: {pos: [75, -430, 50], target: [75, 0, 50], hide: ['radiation_shield', 'sht31_in_shield', 'fan_120', 'fan_guard']},
  bottom: {pos: [75, 35, -430], target: [75, 35, 0], hide: ['radiation_shield', 'sht31_in_shield', 'fan_120', 'fan_guard'], up: [0, -1, 0]},
};
function show(name) {
  const v = views[name] || views.assembly;
  for (const [k, m] of Object.entries(meshes)) m.visible = !v.hide.includes(k);
  camera.up.set(...(v.up || [0, 0, 1])); camera.position.set(...v.pos); orbit.target.set(...v.target); orbit.update();
  document.querySelectorAll('[data-view]').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.view === name)));
}
function size() { const r = host.getBoundingClientRect(); renderer.setSize(r.width, r.height, false); camera.aspect = r.width / r.height; camera.updateProjectionMatrix(); }
addEventListener('resize', size); size();
document.querySelectorAll('[data-view]').forEach(b => b.addEventListener('click', () => { location.hash = b.dataset.view; }));
addEventListener('hashchange', () => show(location.hash.slice(1)));
show(location.hash.slice(1) || 'assembly');
const ray = new THREE.Raycaster(), ptr = new THREE.Vector2();
renderer.domElement.addEventListener('click', ev => {
  if (!info) return; const r = renderer.domElement.getBoundingClientRect();
  ptr.set((ev.clientX - r.left) / r.width * 2 - 1, -(ev.clientY - r.top) / r.height * 2 + 1); ray.setFromCamera(ptr, camera);
  const hit = ray.intersectObjects(Object.values(meshes).filter(m => m.visible), false)[0];
  if (hit) { const p = hit.object.userData, b = p.bounds_mm; info.textContent = `${p.name.replaceAll('_', ' ')} — ${p.note || p.group}. Size ${(b[3] - b[0]).toFixed(1)} × ${(b[4] - b[1]).toFixed(1)} × ${(b[5] - b[2]).toFixed(1)} mm.`; }
});
(function tick() { orbit.update(); renderer.render(scene, camera); requestAnimationFrame(tick); })();
document.body.dataset.ready = '1';
