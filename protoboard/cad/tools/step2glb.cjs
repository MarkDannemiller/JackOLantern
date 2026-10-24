// STEP -> GLB (one glTF node per STEP mesh, named "<path>|<mesh>", STEP colours kept) plus a JSON of bounds.
// Usage: node step2glb.cjs <occt-import-js dir> <in.stp> <out.glb> [--scale 0.001]
// Uses occt-import-js (shipped in the Protoboard stack). Units: STEP mm -> metres when --scale 0.001.
const fs = require("fs"), path = require("path");
const [dir, input, output, ...rest] = process.argv.slice(2);
const scale = rest[0] === "--scale" ? Number(rest[1]) : 1;
require(path.join(dir, "dist/occt-import-js.js"))({ locateFile: (f) => path.join(dir, "dist", f) }).then((occt) => {
  const res = occt.ReadStepFile(new Uint8Array(fs.readFileSync(input)), null);
  if (!res.success) throw new Error("STEP read failed");
  const owner = new Map();
  const walk = (n, trail) => {
    const here = n.name ? [...trail, n.name] : trail;
    for (const i of n.meshes || []) owner.set(i, here.join("/"));
    for (const c of n.children || []) walk(c, here);
  };
  walk(res.root, []);
  const bufs = [], accessors = [], bufferViews = [], meshes = [], nodes = [], materials = [], matIndex = new Map(), bounds = [];
  let offset = 0;
  const push = (typed, target) => {
    const b = Buffer.from(typed.buffer, typed.byteOffset, typed.byteLength);
    const pad = (4 - (b.length % 4)) % 4;
    bufs.push(b, Buffer.alloc(pad));
    bufferViews.push({ buffer: 0, byteOffset: offset, byteLength: b.length, target });
    offset += b.length + pad;
    return bufferViews.length - 1;
  };
  res.meshes.forEach((m, i) => {
    const src = m.attributes.position.array, idx = m.index.array;
    const pos = new Float32Array(src.length), keep = [];
    let finite = true;
    for (let k = 0; k < src.length; k++) { pos[k] = src[k] * scale; if (!Number.isFinite(pos[k])) finite = false; }
    if (!finite || !idx.length) return; // a mesh with non-finite vertices is skipped (reported in bounds)
    const lo = [Infinity, Infinity, Infinity], hi = [-Infinity, -Infinity, -Infinity];
    for (let k = 0; k < pos.length; k += 3) for (let a = 0; a < 3; a++) { lo[a] = Math.min(lo[a], pos[k + a]); hi[a] = Math.max(hi[a], pos[k + a]); }
    const ind = pos.length / 3 > 65535 ? new Uint32Array(idx) : new Uint16Array(idx);
    const pv = push(pos, 34962), iv = push(ind, 34963);
    accessors.push({ bufferView: pv, componentType: 5126, count: pos.length / 3, type: "VEC3", min: lo, max: hi });
    const pa = accessors.length - 1;
    accessors.push({ bufferView: iv, componentType: ind instanceof Uint32Array ? 5125 : 5123, count: ind.length, type: "SCALAR" });
    const ia = accessors.length - 1;
    const c = m.color ? m.color.map((v) => Math.round(v * 1000) / 1000) : [0.7, 0.7, 0.7];
    const key = c.join(",");
    if (!matIndex.has(key)) { materials.push({ name: "step_" + key, pbrMetallicRoughness: { baseColorFactor: [...c, 1], metallicFactor: 0, roughnessFactor: 0.6 } }); matIndex.set(key, materials.length - 1); }
    const name = `${owner.get(i) ?? ""}|${m.name || "mesh" + i}`;
    meshes.push({ name, primitives: [{ attributes: { POSITION: pa }, indices: ia, material: matIndex.get(key) }] });
    nodes.push({ name, mesh: meshes.length - 1 });
    bounds.push({ name, lo, hi, color: c });
  });
  const bin = Buffer.concat(bufs);
  const gltf = { asset: { version: "2.0", generator: "joyful-jack step2glb (occt-import-js)" }, scene: 0, scenes: [{ nodes: nodes.map((_, i) => i) }], nodes, meshes, materials, accessors, bufferViews, buffers: [{ byteLength: bin.length }] };
  let json = Buffer.from(JSON.stringify(gltf));
  json = Buffer.concat([json, Buffer.alloc((4 - (json.length % 4)) % 4, 0x20)]);
  const header = Buffer.alloc(12), jh = Buffer.alloc(8), bh = Buffer.alloc(8);
  header.writeUInt32LE(0x46546c67, 0); header.writeUInt32LE(2, 4); header.writeUInt32LE(12 + 8 + json.length + 8 + bin.length, 8);
  jh.writeUInt32LE(json.length, 0); jh.writeUInt32LE(0x4e4f534a, 4); bh.writeUInt32LE(bin.length, 0); bh.writeUInt32LE(0x004e4942, 4);
  fs.writeFileSync(output, Buffer.concat([header, jh, json, bh, bin]));
  fs.writeFileSync(output.replace(/\.glb$/, ".bounds.json"), JSON.stringify({ scale, meshes: bounds }, null, 1));
  console.log(`wrote ${output}: ${nodes.length} meshes (${res.meshes.length - nodes.length} skipped)`);
});
